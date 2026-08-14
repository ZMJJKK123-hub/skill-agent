package net.minecraft.client.resources.model;

import java.util.List;
import net.minecraft.client.renderer.block.model.BlockModelPart;
import net.minecraft.client.renderer.block.model.BlockStateModel;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.util.RandomSource;
import net.minecraft.util.random.Weighted;
import net.minecraft.util.random.WeightedList;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class WeightedVariants implements BlockStateModel {
    private final WeightedList<BlockStateModel> list;
    private final BlockStateModel firstModel;
    private final TextureAtlasSprite particleIcon;

    public WeightedVariants(WeightedList<BlockStateModel> p_394939_) {
        this.list = p_394939_;
        this.firstModel = p_394939_.unwrap().getFirst().value();
        this.particleIcon = firstModel.particleIcon();
    }

    @Override
    public TextureAtlasSprite particleIcon() {
        return this.particleIcon;
    }

    @Override
    public TextureAtlasSprite particleIcon(net.minecraftforge.client.model.data.ModelData data) {
        return this.firstModel.particleIcon(data);
    }

    @Override
    public void collectParts(RandomSource p_397916_, List<BlockModelPart> p_394308_) {
        this.list.getRandomOrThrow(p_397916_).collectParts(p_397916_, p_394308_);
    }

    @Override
    public void collectParts(RandomSource random, List<BlockModelPart> dest, net.minecraftforge.client.model.data.ModelData data, net.minecraft.client.renderer.chunk.ChunkSectionLayer renderType) {
        this.list.getRandomOrThrow(random).collectParts(random, dest, data, renderType);
    }

    @Override
    public java.util.Collection<net.minecraft.client.renderer.chunk.ChunkSectionLayer> getRenderTypes(net.minecraft.world.level.block.state.BlockState state, RandomSource random, net.minecraftforge.client.model.data.ModelData data) {
        return this.list.getRandomOrThrow(random).getRenderTypes(state, random, data);
    }

    @OnlyIn(Dist.CLIENT)
    public record Unbaked(WeightedList<BlockStateModel.Unbaked> entries) implements BlockStateModel.Unbaked {
        @Override
        public BlockStateModel bake(ModelBaker p_392595_) {
            return new WeightedVariants(this.entries.map(p_396925_ -> p_396925_.bake(p_392595_)));
        }

        @Override
        public void resolveDependencies(ResolvableModel.Resolver p_392817_) {
            this.entries.unwrap().forEach(p_393012_ -> p_393012_.value().resolveDependencies(p_392817_));
        }
    }
}
