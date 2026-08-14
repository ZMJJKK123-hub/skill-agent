package net.minecraft.server.jsonrpc.api;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.mojang.serialization.codecs.RecordCodecBuilder.Instance;

public record ResultInfo<Result>(String name, Schema<Result> schema) {
    public static <Result> Codec<ResultInfo<Result>> typedCodec() {
        return RecordCodecBuilder.create(
            p_449119_ -> p_449119_.group(
                    Codec.STRING.fieldOf("name").forGetter(ResultInfo::name),
                    Schema.<Result>typedCodec().fieldOf("schema").forGetter(ResultInfo::schema)
                )
                .apply(p_449119_, ResultInfo::new)
        );
    }
}
