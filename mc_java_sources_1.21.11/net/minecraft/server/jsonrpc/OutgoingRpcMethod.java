package net.minecraft.server.jsonrpc;

import com.google.gson.JsonElement;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.jsonrpc.api.MethodInfo;
import net.minecraft.server.jsonrpc.api.ParamInfo;
import net.minecraft.server.jsonrpc.api.ResultInfo;
import net.minecraft.server.jsonrpc.api.Schema;
import org.jspecify.annotations.Nullable;

public interface OutgoingRpcMethod<Params, Result> {
    String NOTIFICATION_PREFIX = "notification/";

    MethodInfo<Params, Result> info();

    OutgoingRpcMethod.Attributes attributes();

    default @Nullable JsonElement encodeParams(Params p_431028_) {
        return null;
    }

    default @Nullable Result decodeResult(JsonElement p_426415_) {
        return null;
    }

    static OutgoingRpcMethod.OutgoingRpcMethodBuilder<Void, Void> notification() {
        return new OutgoingRpcMethod.OutgoingRpcMethodBuilder<>(OutgoingRpcMethod.ParmeterlessNotification::new);
    }

    static <Params> OutgoingRpcMethod.OutgoingRpcMethodBuilder<Params, Void> notificationWithParams() {
        return new OutgoingRpcMethod.OutgoingRpcMethodBuilder<>(OutgoingRpcMethod.Notification::new);
    }

    static <Result> OutgoingRpcMethod.OutgoingRpcMethodBuilder<Void, Result> request() {
        return new OutgoingRpcMethod.OutgoingRpcMethodBuilder<>(OutgoingRpcMethod.ParameterlessMethod::new);
    }

    static <Params, Result> OutgoingRpcMethod.OutgoingRpcMethodBuilder<Params, Result> requestWithParams() {
        return new OutgoingRpcMethod.OutgoingRpcMethodBuilder<>(OutgoingRpcMethod.Method::new);
    }

    public record Attributes(boolean discoverable) {
    }

    @FunctionalInterface
    public interface Factory<Params, Result> {
        OutgoingRpcMethod<Params, Result> create(MethodInfo<Params, Result> p_430664_, OutgoingRpcMethod.Attributes p_425247_);
    }

    public record Method<Params, Result>(MethodInfo<Params, Result> info, OutgoingRpcMethod.Attributes attributes)
        implements OutgoingRpcMethod<Params, Result> {
        @Override
        public @Nullable JsonElement encodeParams(Params p_431477_) {
            if (this.info.params().isEmpty()) {
                throw new IllegalStateException("Method defined as having no parameters");
            } else {
                return this.info.params().get().schema().codec().encodeStart(JsonOps.INSTANCE, p_431477_).getOrThrow();
            }
        }

        @Override
        public Result decodeResult(JsonElement p_426216_) {
            if (this.info.result().isEmpty()) {
                throw new IllegalStateException("Method defined as having no result");
            } else {
                return this.info.result().get().schema().codec().parse(JsonOps.INSTANCE, p_426216_).getOrThrow();
            }
        }

        @Override
        public MethodInfo<Params, Result> info() {
            return this.info;
        }

        @Override
        public OutgoingRpcMethod.Attributes attributes() {
            return this.attributes;
        }
    }

    public record Notification<Params>(MethodInfo<Params, Void> info, OutgoingRpcMethod.Attributes attributes) implements OutgoingRpcMethod<Params, Void> {
        @Override
        public @Nullable JsonElement encodeParams(Params p_424475_) {
            if (this.info.params().isEmpty()) {
                throw new IllegalStateException("Method defined as having no parameters");
            } else {
                return this.info.params().get().schema().codec().encodeStart(JsonOps.INSTANCE, p_424475_).getOrThrow();
            }
        }

        @Override
        public MethodInfo<Params, Void> info() {
            return this.info;
        }

        @Override
        public OutgoingRpcMethod.Attributes attributes() {
            return this.attributes;
        }
    }

    public static class OutgoingRpcMethodBuilder<Params, Result> {
        public static final OutgoingRpcMethod.Attributes DEFAULT_ATTRIBUTES = new OutgoingRpcMethod.Attributes(true);
        private final OutgoingRpcMethod.Factory<Params, Result> method;
        private String description = "";
        private @Nullable ParamInfo<Params> paramInfo;
        private @Nullable ResultInfo<Result> resultInfo;

        public OutgoingRpcMethodBuilder(OutgoingRpcMethod.Factory<Params, Result> p_424582_) {
            this.method = p_424582_;
        }

        public OutgoingRpcMethod.OutgoingRpcMethodBuilder<Params, Result> description(String p_426554_) {
            this.description = p_426554_;
            return this;
        }

        public OutgoingRpcMethod.OutgoingRpcMethodBuilder<Params, Result> response(String p_458583_, Schema<Result> p_453663_) {
            this.resultInfo = new ResultInfo<>(p_458583_, p_453663_);
            return this;
        }

        public OutgoingRpcMethod.OutgoingRpcMethodBuilder<Params, Result> param(String p_454653_, Schema<Params> p_457097_) {
            this.paramInfo = new ParamInfo<>(p_454653_, p_457097_);
            return this;
        }

        private OutgoingRpcMethod<Params, Result> build() {
            MethodInfo<Params, Result> methodinfo = new MethodInfo<>(this.description, this.paramInfo, this.resultInfo);
            return this.method.create(methodinfo, DEFAULT_ATTRIBUTES);
        }

        public Holder.Reference<OutgoingRpcMethod<Params, Result>> register(String p_423728_) {
            return this.register(Identifier.withDefaultNamespace("notification/" + p_423728_));
        }

        private Holder.Reference<OutgoingRpcMethod<Params, Result>> register(Identifier p_453388_) {
            return Registry.registerForHolder(BuiltInRegistries.OUTGOING_RPC_METHOD, p_453388_, this.build());
        }
    }

    public record ParameterlessMethod<Result>(MethodInfo<Void, Result> info, OutgoingRpcMethod.Attributes attributes)
        implements OutgoingRpcMethod<Void, Result> {
        @Override
        public Result decodeResult(JsonElement p_426562_) {
            if (this.info.result().isEmpty()) {
                throw new IllegalStateException("Method defined as having no result");
            } else {
                return this.info.result().get().schema().codec().parse(JsonOps.INSTANCE, p_426562_).getOrThrow();
            }
        }

        @Override
        public MethodInfo<Void, Result> info() {
            return this.info;
        }

        @Override
        public OutgoingRpcMethod.Attributes attributes() {
            return this.attributes;
        }
    }

    public record ParmeterlessNotification(MethodInfo<Void, Void> info, OutgoingRpcMethod.Attributes attributes) implements OutgoingRpcMethod<Void, Void> {
        @Override
        public MethodInfo<Void, Void> info() {
            return this.info;
        }

        @Override
        public OutgoingRpcMethod.Attributes attributes() {
            return this.attributes;
        }
    }
}
