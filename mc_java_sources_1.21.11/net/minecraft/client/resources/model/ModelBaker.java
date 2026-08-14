package net.minecraft.client.resources.model;

import net.minecraft.client.renderer.block.model.BlockModelPart;
import net.minecraft.resources.Identifier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3f;
import org.joml.Vector3fc;

@OnlyIn(Dist.CLIENT)
public interface ModelBaker {
    ResolvedModel getModel(Identifier p_456994_);

    BlockModelPart missingBlockModelPart();

    SpriteGetter sprites();

    ModelBaker.PartCache parts();

    <T> T compute(ModelBaker.SharedOperationKey<T> p_395456_);

    @OnlyIn(Dist.CLIENT)
    public interface PartCache {
        default Vector3fc vector(float p_452065_, float p_451254_, float p_452365_) {
            return this.vector(new Vector3f(p_452065_, p_451254_, p_452365_));
        }

        Vector3fc vector(Vector3fc p_460548_);
    }

    @FunctionalInterface
    @OnlyIn(Dist.CLIENT)
    public interface SharedOperationKey<T> {
        T compute(ModelBaker p_393089_);
    }

    /** Forge: Return the render type to use when baking this model, its a dirty hack to pass down this value to parents */
    @org.jetbrains.annotations.Nullable
    default net.minecraftforge.client.RenderTypeGroup renderType() {
        return null;
    }

    /** Forge: Return the fast graphics render type to use when baking this model, its a dirty hack to pass down this value to parents */
    @org.jetbrains.annotations.Nullable
    default net.minecraftforge.client.RenderTypeGroup renderTypeFast() {
        return null;
    }
}
