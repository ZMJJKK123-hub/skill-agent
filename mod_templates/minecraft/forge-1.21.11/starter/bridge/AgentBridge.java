package com.agentbridge;

// ============================================================================
// AgentBridge —— 进程内 UI 自动化桥（免窗口焦点、免模拟鼠标）
//
// 用法（agent 按此操作，共两步）：
//   1. 把本文件复制到 src/test/java/com/agentbridge/AgentBridge.java
//   2. 在你的主 @Mod 类构造器末尾加一行（构造器自订阅 tick 事件总线）：
//        new com.agentbridge.AgentBridge();
//   然后用 run_test_client（测试源码集在 classpath 上；run_client 不行）启动
//   客户端，之后用 bridge_command 工具下发命令：
//     screen_info            → 当前界面类名 + 全部按钮/控件列表（index/文字/可用性）
//     click {index}          → 直接调用该按钮背后的 onPress(...)（不是模拟鼠标）
//     set_text {index,value} → 设置输入框（EditBox）内容
//     chat {text}            → 发送聊天/命令（"/give @s ..."）
//     screenshot {name}      → 用游戏渲染器截图（后台窗口也能截，存 run/agent_shots/）
//
// 协议：命令文件 run/bridge_cmd.json（含唯一 id），处理后写 run/bridge_result.json
//（同 id），并删除命令文件。轮询在客户端每 tick 执行，延迟 <50ms。
// 本文件属测试源码集，不会打进发布 jar。
// ============================================================================

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.events.ContainerEventHandler;
import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.input.MouseButtonInfo;
import net.minecraftforge.event.TickEvent;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class AgentBridge {

    private final Minecraft mc = Minecraft.getInstance();

    public AgentBridge() {
        // 本 Forge(eventbus 7) 为"每事件一条总线"：事件类自带静态 BUS，
        // addListener(Consumer) 订阅——没有老版的 register(Object)+@SubscribeEvent。
        TickEvent.ClientTickEvent.Post.BUS.addListener(this::onClientTick);
    }

    private void onClientTick(TickEvent.ClientTickEvent.Post event) {
        try {
            poll();
        } catch (Throwable t) {
            // 桥自身任何异常都不能影响游戏主循环
            System.out.println("[AgentBridge] error: " + t);
        }
    }

    private void poll() throws Exception {
        Path run = Paths.get("run");
        Files.createDirectories(run);
        Path cmdPath = run.resolve("bridge_cmd.json");
        if (!Files.exists(cmdPath)) return;
        String raw = Files.readString(cmdPath, StandardCharsets.UTF_8);
        JsonObject cmd = new GsonBuilder().create().fromJson(raw, JsonObject.class);
        Files.delete(cmdPath); // 处理即删，防重复消费

        JsonObject result = new JsonObject();
        result.addProperty("id", cmd.has("id") ? cmd.get("id").getAsString() : "");
        result.addProperty("op", cmd.has("op") ? cmd.get("op").getAsString() : "");
        try {
            handle(cmd, result);
            result.addProperty("ok", true);
        } catch (Throwable t) {
            result.addProperty("ok", false);
            result.addProperty("error", String.valueOf(t));
        }
        Files.writeString(run.resolve("bridge_result.json"),
                new GsonBuilder().setPrettyPrinting().create().toJson(result),
                StandardCharsets.UTF_8);
    }

    private void handle(JsonObject cmd, JsonObject out) throws Exception {
        String op = cmd.get("op").getAsString();
        switch (op) {
            case "screen_info" -> {
                Screen screen = mc.screen;
                out.addProperty("in_world", mc.level != null && mc.player != null);
                if (screen == null) {
                    out.addProperty("screen", "");
                } else {
                    out.addProperty("screen", screen.getClass().getSimpleName());
                    List<AbstractWidget> widgets = new ArrayList<>();
                    collect(screen, widgets, 0);
                    JsonArray arr = new JsonArray();
                    for (int i = 0; i < widgets.size(); i++) {
                        AbstractWidget w = widgets.get(i);
                        JsonObject o = new JsonObject();
                        o.addProperty("index", i);
                        o.addProperty("type", w.getClass().getSimpleName());
                        o.addProperty("label", w.getMessage() == null ? "" : w.getMessage().getString());
                        o.addProperty("active", w.active);
                        o.addProperty("visible", w.visible);
                        o.addProperty("editable", w instanceof EditBox);
                        arr.add(o);
                    }
                    out.add("widgets", arr);
                }
            }
            case "click" -> {
                int index = cmd.get("index").getAsInt();
                AbstractWidget w = widgetAt(index);
                if (w == null) throw new IllegalStateException("no widget at index " + index);
                if (!(w instanceof AbstractButton btn))
                    throw new IllegalStateException("widget " + index + " (" + w.getClass().getSimpleName() + ") is not a button");
                // 直接调用按钮回调本身——即鼠标点击最终执行的那个函数
                btn.onPress(new MouseButtonEvent(0, 0, new MouseButtonInfo(0, 0)));
                out.addProperty("clicked", w.getMessage() == null ? "" : w.getMessage().getString());
            }
            case "set_text" -> {
                int index = cmd.get("index").getAsInt();
                String value = cmd.get("value").getAsString();
                AbstractWidget w = widgetAt(index);
                if (!(w instanceof EditBox box))
                    throw new IllegalStateException("widget " + index + " is not an EditBox");
                box.setValue(value);
                out.addProperty("set", value);
            }
            case "chat" -> {
                String text = cmd.get("text").getAsString();
                if (mc.getConnection() == null)
                    throw new IllegalStateException("no connection (not in a world?)");
                if (text.startsWith("/")) {
                    mc.getConnection().sendCommand(text.substring(1));
                } else {
                    mc.getConnection().sendChat(text);
                }
                out.addProperty("sent", text);
            }
            case "screenshot" -> {
                String name = cmd.has("name") && !cmd.get("name").getAsString().isBlank()
                        ? cmd.get("name").getAsString()
                        : "bridge_" + UUID.randomUUID().toString().substring(0, 8);
                File dir = new File("run/agent_shots");
                dir.mkdirs();
                File file = new File(dir, name.endsWith(".png") ? name : name + ".png");
                Screenshot.grab(file, mc.getMainRenderTarget(), c -> {});
                out.addProperty("path", file.getAbsolutePath());
            }
            default -> throw new IllegalStateException("unknown op: " + op);
        }
    }

    /** 收集当前界面的全部控件（含容器内嵌一层），index 即 click/set_text 的下标。 */
    private void collect(GuiEventListener node, List<AbstractWidget> out, int depth) {
        if (node instanceof AbstractWidget aw) out.add(aw);
        if (depth >= 2) return;
        if (node instanceof ContainerEventHandler ceh) {
            for (GuiEventListener child : ceh.children()) collect(child, out, depth + 1);
        }
    }

    private List<AbstractWidget> widgetsNow() {
        List<AbstractWidget> list = new ArrayList<>();
        if (mc.screen != null) collect(mc.screen, list, 0);
        return list;
    }

    private AbstractWidget widgetAt(int index) {
        List<AbstractWidget> list = widgetsNow();
        return (index >= 0 && index < list.size()) ? list.get(index) : null;
    }

    /** 主 mod 构造器里挂载用：new AgentBridge();（构造器自订阅） */
    public static void noop() {}
}
