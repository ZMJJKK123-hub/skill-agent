package net.minecraft.client.renderer.block.model;

import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3fc;

@OnlyIn(Dist.CLIENT)
public record BakedQuad(
    Vector3fc position0,
    Vector3fc position1,
    Vector3fc position2,
    Vector3fc position3,
    long packedUV0,
    long packedUV1,
    long packedUV2,
    long packedUV3,
    int tintIndex,
    Direction direction,
    TextureAtlasSprite sprite,
    boolean shade,
    int lightEmission,
    boolean ambientOcclusion
) {
    public static final int VERTEX_COUNT = 4;

    public BakedQuad(
        Vector3fc position0, Vector3fc position1, Vector3fc position2, Vector3fc position3,
        long packedUV0, long packedUV1, long packedUV2, long packedUV3,
        int tintIndex, Direction direction, TextureAtlasSprite sprite, boolean shade, int lightEmission) {
        this(position0, position1, position2, position3, packedUV0, packedUV1, packedUV2, packedUV3, tintIndex, direction, sprite, shade, lightEmission, true);
    }

    public boolean isTinted() {
        return this.tintIndex != -1;
    }

    public Vector3fc position(int p_459790_) {
        return switch (p_459790_) {
            case 0 -> this.position0;
            case 1 -> this.position1;
            case 2 -> this.position2;
            case 3 -> this.position3;
            default -> throw new IndexOutOfBoundsException(p_459790_);
        };
    }

    public long packedUV(int p_455420_) {
        return switch (p_455420_) {
            case 0 -> this.packedUV0;
            case 1 -> this.packedUV1;
            case 2 -> this.packedUV2;
            case 3 -> this.packedUV3;
            default -> throw new IndexOutOfBoundsException(p_455420_);
        };
    }
}
