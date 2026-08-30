package com.agentbridge;

// ============================================================================
// AgentBridge —— 进程内 UI 自动化桥（免窗口焦点、免模拟鼠标）
//
// 用法（agent 按此操作，共两步）：
//   1. 把本文件复制到 src/main/java/com/agentbridge/AgentBridge.java
//      （必须放 main 源集：test 源集在 SECURE-BOOTSTRAP 模块加载器里，
//        Minecraft/eventbus 类是重复副本，LinkageError + 静态实例读空——
//        webserv_moonstone 实测；main 与主 mod 同加载器，无此问题）
//   2. 主 @Mod 构造器末尾加一行：new com.agentbridge.AgentBridge();
//      （生产 jar 内本类自动失活：构造器检测工作区无 build.gradle 即返回）
//   客户端用 start_mc_client 启动即可（无需 test 客户端），配合 bridge_command：
//     screen_info / click / set_text / chat / screenshot（详见各 op 注释）
//
// 协议：命令文件 run/bridge_cmd.json（含唯一 id）→ 处理后写 run/bridge_result.json
//（同 id）并删命令文件。独立守护线程 50ms 轮询，不依赖任何 forge 事件。
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

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class AgentBridge {

    private Minecraft mc() { return Minecraft.getInstance(); }

    public AgentBridge() {
        // 生产环境守卫：真实玩家目录（含其上级）没有 build.gradle，直接失活（不启线程）。
        // 注意 dev 客户端 CWD 是 <项目>/run，build.gradle 在上一级——两级都要探测。
        boolean devWorkspace = java.nio.file.Paths.get("build.gradle").toFile().exists()
                || java.nio.file.Paths.get("..", "build.gradle").toFile().exists();
        if (!devWorkspace) return;
        // 独立守护线程 50ms 轮询命令文件——零 forge 事件链接（test 模块加载器的
        // eventbus 类与 app 加载器重复，事件订阅会 LinkageError，实测）
        Thread t = new Thread(() -> {
            System.out.println("[AgentBridge] armed (cmd dir: " + resolveRunDir() + ")");
            while (true) {
                try {
                    poll();
                } catch (Throwable e) {
                    System.out.println("[AgentBridge] poll error: " + e);
                }
                try { Thread.sleep(50); } catch (InterruptedException ie) { return; }
            }
        }, "agentbridge-poller");
        t.setDaemon(true);
        t.start();
    }

    /** 客户端 CWD 可能是项目根，也可能就是 <项目>/run（dev run 默认）——两者都兼容。 */
    private static Path resolveRunDir() {
        Path here = Paths.get("").toAbsolutePath();
        if (here.getFileName() != null && "run".equals(here.getFileName().toString())) return here;
        return here.resolve("run");
    }

    private void poll() throws Exception {
        Path run = resolveRunDir();
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

    /** 变更类操作必须跑在客户端主线程（RenderSystem 断言），经 mc().execute 投递。 */
    private void handle(JsonObject cmd, JsonObject out) throws Exception {
        String op = cmd.get("op").getAsString();
        if ("screen_info".equals(op)) {
            doScreenInfo(out);
            return;
        }
        java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(1);
        java.util.concurrent.atomic.AtomicReference<Throwable> err = new java.util.concurrent.atomic.AtomicReference<>();
        mc().execute(() -> {
            try {
                doOp(cmd, op, out);
            } catch (Throwable t) {
                err.set(t);
            } finally {
                latch.countDown();
            }
        });
        if (!latch.await(6, java.util.concurrent.TimeUnit.SECONDS))
            throw new IllegalStateException("client thread busy (op timeout)");
        if (err.get() != null) throw new RuntimeException(err.get());
    }

    private void doScreenInfo(JsonObject out) {
        Screen screen = mc().screen;
        out.addProperty("in_world", mc().level != null && mc().player != null);
        if (screen == null) {
            out.addProperty("screen", "");
        } else {
            out.addProperty("screen", screen.getClass().getSimpleName());
            java.util.List<AbstractWidget> widgets = new java.util.ArrayList<>();
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

    private void doOp(JsonObject cmd, String op, JsonObject out) throws Exception {
        switch (op) {
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
                if (mc().getConnection() == null)
                    throw new IllegalStateException("no connection (not in a world?)");
                if (text.startsWith("/")) {
                    mc().getConnection().sendCommand(text.substring(1));
                } else {
                    mc().getConnection().sendChat(text);
                }
                out.addProperty("sent", text);
            }
            case "screenshot" -> {
                // grab 的 File 是【目录】语义：实际写入 <dir>/screenshots/<时间戳>.png，
                // 且必须在渲染线程调用（takeScreenshot 直读帧缓冲）。异步落盘由
                // ioPool 完成——调用方按 mtime 轮询取新文件。
                File dir = new File(resolveRunDir().toFile(), "agent_shots");
                dir.mkdirs();
                Screenshot.grab(dir, null, mc().getMainRenderTarget(), 1, c -> {});
                out.addProperty("path", new File(dir, "screenshots").getAbsolutePath());
                out.addProperty("note", "async: newest .png under path lands within ~2s");
            }
            case "interact" -> {
                // 右键世界交互。优先显式坐标 x/y/z（或 below=脚下方块），构造确定命中；
                // 缺省才用 player.pick（视线在眼睛高度，常 MISS 脚部方块，实测）。
                var player = mc().player;
                if (player == null) throw new IllegalStateException("not in world");
                net.minecraft.world.phys.BlockHitResult hit;
                if (cmd.has("x")) {
                    var pos = new net.minecraft.core.BlockPos(cmd.get("x").getAsInt(),
                            cmd.get("y").getAsInt(), cmd.get("z").getAsInt());
                    var dir = cmd.has("dir") ? net.minecraft.core.Direction.byName(cmd.get("dir").getAsString())
                            : net.minecraft.core.Direction.UP;
                    hit = new net.minecraft.world.phys.BlockHitResult(
                            net.minecraft.world.phys.Vec3.atCenterOf(pos), dir, pos, false);
                } else if ("below".equals(cmd.has("where") ? cmd.get("where").getAsString() : "")) {
                    var pos = net.minecraft.core.BlockPos.containing(player.getX(), player.getY(), player.getZ()).below();
                    hit = new net.minecraft.world.phys.BlockHitResult(
                            net.minecraft.world.phys.Vec3.atCenterOf(pos), net.minecraft.core.Direction.UP, pos, false);
                } else {
                    var picked = player.pick(4.5, 1.0F, false);
                    if (!(picked instanceof net.minecraft.world.phys.BlockHitResult bhr))
                        throw new IllegalStateException("pick missed (use explicit x/y/z)");
                    hit = bhr;
                }
                var r = mc().gameMode.useItemOn(player, net.minecraft.world.InteractionHand.MAIN_HAND, hit);
                if (!r.consumesAction()) {
                    // gameMode 层被拦时兜底：直接跑客户端 useWithoutItem + 手动发交互包
                    //（服务端才是 openMenu 的执行方，包必须送达）
                    var bs = mc().level.getBlockState(hit.getBlockPos());
                    r = bs.useWithoutItem(mc().level, player, hit);
                    try {
                        mc().getConnection().send(new net.minecraft.network.protocol.game.ServerboundUseItemOnPacket(
                                net.minecraft.world.InteractionHand.MAIN_HAND, hit, 0));
                    } catch (Throwable ignore) {}
                }
                out.addProperty("result", String.valueOf(r));
                out.addProperty("target", hit.getBlockPos().toString());
            }
            case "close_screen" -> {
                // 关闭当前界面（等价 ESC 确认动作），零键盘依赖
                var s = mc().screen;
                if (s == null) throw new IllegalStateException("no screen open");
                s.onClose();
                out.addProperty("closed", s.getClass().getSimpleName());
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
        if (mc().screen != null) collect(mc().screen, list, 0);
        return list;
    }

    private AbstractWidget widgetAt(int index) {
        List<AbstractWidget> list = widgetsNow();
        return (index >= 0 && index < list.size()) ? list.get(index) : null;
    }

    /** 主 mod 构造器里挂载用：new AgentBridge();（构造器自订阅） */
    public static void noop() {}
}
