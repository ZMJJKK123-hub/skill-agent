package net.minecraft.client.renderer.special;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.serialization.MapCodec;
import java.util.function.Consumer;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.PlayerSkinRenderCache;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.resources.model.MaterialSet;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface SpecialModelRenderer<T> {
    void submit(
        @Nullable T p_378499_,
        ItemDisplayContext p_377312_,
        PoseStack p_378346_,
        SubmitNodeCollector p_426743_,
        int p_377547_,
        int p_378601_,
        boolean p_376553_,
        int p_431907_
    );

    void getExtents(Consumer<Vector3fc> p_457786_);

    @Nullable T extractArgument(ItemStack p_376218_);

    @OnlyIn(Dist.CLIENT)
    public interface BakingContext {
        EntityModelSet entityModelSet();

        MaterialSet materials();

        PlayerSkinRenderCache playerSkinRenderCache();

        @OnlyIn(Dist.CLIENT)
        public record Simple(EntityModelSet entityModelSet, MaterialSet materials, PlayerSkinRenderCache playerSkinRenderCache) implements SpecialModelRenderer.BakingContext {
            @Override
            public EntityModelSet entityModelSet() {
                return this.entityModelSet;
            }

            @Override
            public MaterialSet materials() {
                return this.materials;
            }

            @Override
            public PlayerSkinRenderCache playerSkinRenderCache() {
                return this.playerSkinRenderCache;
            }
        }
    }

    @OnlyIn(Dist.CLIENT)
    public interface Unbaked {
        @Nullable SpecialModelRenderer<?> bake(SpecialModelRenderer.BakingContext p_425902_);

        MapCodec<? extends SpecialModelRenderer.Unbaked> type();
    }
}
