package net.minecraft.core;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;

public interface ClientAsset {
    Identifier id();

    public record DownloadedTexture(Identifier texturePath, String url) implements ClientAsset.Texture {
        @Override
        public Identifier id() {
            return this.texturePath;
        }

        @Override
        public Identifier texturePath() {
            return this.texturePath;
        }
    }

    public record ResourceTexture(Identifier id, Identifier texturePath) implements ClientAsset.Texture {
        public static final Codec<ClientAsset.ResourceTexture> CODEC = Identifier.CODEC
            .xmap(ClientAsset.ResourceTexture::new, ClientAsset.ResourceTexture::id);
        public static final MapCodec<ClientAsset.ResourceTexture> DEFAULT_FIELD_CODEC = CODEC.fieldOf("asset_id");
        public static final StreamCodec<ByteBuf, ClientAsset.ResourceTexture> STREAM_CODEC = Identifier.STREAM_CODEC
            .map(ClientAsset.ResourceTexture::new, ClientAsset.ResourceTexture::id);

        public ResourceTexture(Identifier p_460018_) {
            this(p_460018_, p_460018_.withPath(p_425999_ -> "textures/" + p_425999_ + ".png"));
        }

        @Override
        public Identifier id() {
            return this.id;
        }

        @Override
        public Identifier texturePath() {
            return this.texturePath;
        }
    }

    public interface Texture extends ClientAsset {
        Identifier texturePath();
    }
}
