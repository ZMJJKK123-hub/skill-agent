package net.minecraft.world.level.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ScheduledTickAccess;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraftforge.common.IPlantable;

public abstract class VegetationBlock extends Block implements IPlantable {
   protected VegetationBlock(BlockBehaviour.Properties properties) {
      super(properties);
   }

   @Override
   protected abstract MapCodec<? extends VegetationBlock> codec();

   protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
      return state.is(BlockTags.SUPPORTS_VEGETATION) || state.getBlock() instanceof FarmlandBlock;
   }

   @Override
   protected BlockState updateShape(
      BlockState state,
      LevelReader level,
      ScheduledTickAccess ticks,
      BlockPos pos,
      Direction directionToNeighbour,
      BlockPos neighbourPos,
      BlockState neighbourState,
      RandomSource random
   ) {
      return !state.canSurvive(level, pos)
         ? Blocks.AIR.defaultBlockState()
         : super.updateShape(state, level, ticks, pos, directionToNeighbour, neighbourPos, neighbourState, random);
   }

   @Override
   protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
      BlockPos below = pos.below();
      return state.getBlock() == this
         ? level.getBlockState(below).canSustainPlant(level, below, Direction.UP, this)
         : this.mayPlaceOn(level.getBlockState(below), level, below);
   }

   @Override
   protected boolean propagatesSkylightDown(BlockState state) {
      return state.getFluidState().isEmpty();
   }

   @Override
   protected boolean isPathfindable(BlockState state, PathComputationType type) {
      return type == PathComputationType.AIR && !this.hasCollision ? true : super.isPathfindable(state, type);
   }

   @Override
   public BlockState getPlant(BlockGetter world, BlockPos pos) {
      BlockState state = world.getBlockState(pos);
      return state.getBlock() == this ? state : this.defaultBlockState();
   }
}
