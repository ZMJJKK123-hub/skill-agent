package net.minecraft.client.renderer.block.model;

import com.mojang.serialization.Codec;
import java.util.List;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class SingleVariant implements BlockStateModel {
    private final BlockModelPart model;
    private final java.util.Collection<net.minecraft.client.renderer.chunk.ChunkSectionLayer> layer;
    private final java.util.Collection<net.minecraft.client.renderer.chunk.ChunkSectionLayer> layerFast;

    public SingleVariant(BlockModelPart p_394592_) {
        this.model = p_394592_;
        this.layer = this.model.layer() == null ? null : java.util.EnumSet.of(this.model.layer());
        this.layerFast = this.model.layerFast() == null ? null : java.util.EnumSet.of(this.model.layerFast());
    }

    @Override
    public void collectParts(RandomSource p_397567_, List<BlockModelPart> p_396765_) {
        p_396765_.add(this.model);
    }

    @Override
    public TextureAtlasSprite particleIcon() {
        return this.model.particleIcon();
    }

    @Override
    public java.util.Collection<net.minecraft.client.renderer.chunk.ChunkSectionLayer> getRenderTypes(net.minecraft.world.level.block.state.BlockState state, RandomSource rand, net.minecraftforge.client.model.data.ModelData data) {
        var type = net.minecraft.client.renderer.ItemBlockRenderTypes.isFancy() ? layer : layerFast;
        return type != null ? type : BlockStateModel.super.getRenderTypes(state, rand, data);
    }

    @OnlyIn(Dist.CLIENT)
    public record Unbaked(Variant variant) implements BlockStateModel.Unbaked {
        public static final Codec<SingleVariant.Unbaked> CODEC = Variant.CODEC.xmap(SingleVariant.Unbaked::new, SingleVariant.Unbaked::variant);

        @Override
        public BlockStateModel bake(ModelBaker p_397283_) {
            return new SingleVariant(this.variant.bake(p_397283_));
        }

        @Override
        public void resolveDependencies(ResolvableModel.Resolver p_395676_) {
            this.variant.resolveDependencies(p_395676_);
        }
    }
}
