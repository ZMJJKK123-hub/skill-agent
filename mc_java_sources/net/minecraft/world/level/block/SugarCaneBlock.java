package net.minecraft.world.level.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ScheduledTickAccess;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.IPlantable;
import net.minecraftforge.common.PlantType;

public class SugarCaneBlock extends Block implements IPlantable {
   public static final MapCodec<SugarCaneBlock> CODEC = simpleCodec(SugarCaneBlock::new);
   public static final IntegerProperty AGE = BlockStateProperties.AGE_15;
   private static final VoxelShape SHAPE = Block.column(12.0, 0.0, 16.0);

   @Override
   public MapCodec<SugarCaneBlock> codec() {
      return CODEC;
   }

   public SugarCaneBlock(BlockBehaviour.Properties properties) {
      super(properties);
      this.registerDefaultState(this.stateDefinition.any().setValue(AGE, 0));
   }

   @Override
   protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
      return SHAPE;
   }

   @Override
   protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
      if (!state.canSurvive(level, pos)) {
         level.destroyBlock(pos, true);
      }
   }

   @Override
   protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
      if (level.isEmptyBlock(pos.above())) {
         int height = 1;

         while (level.getBlockState(pos.below(height)).is(this)) {
            height++;
         }

         if (height < 3) {
            int age = state.getValue(AGE);
            if (ForgeHooks.onCropsGrowPre(level, pos, state, true)) {
               if (age == 15) {
                  level.setBlockAndUpdate(pos.above(), this.defaultBlockState());
                  ForgeHooks.onCropsGrowPost(level, pos.above(), this.defaultBlockState());
                  level.setBlock(pos, state.setValue(AGE, 0), 260);
               } else {
                  level.setBlock(pos, state.setValue(AGE, age + 1), 260);
               }
            }
         }
      }
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
      if (!state.canSurvive(level, pos)) {
         ticks.scheduleTick(pos, this, 1);
      }

      return super.updateShape(state, level, ticks, pos, directionToNeighbour, neighbourPos, neighbourState, random);
   }

   @Override
   protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
      BlockState soil = level.getBlockState(pos.below());
      if (soil.canSustainPlant(level, pos.below(), Direction.UP, this)) {
         return true;
      }

      BlockState stateBelow = level.getBlockState(pos.below());
      if (stateBelow.is(this)) {
         return true;
      }

      if (stateBelow.is(BlockTags.SUPPORTS_SUGAR_CANE)) {
         BlockPos below = pos.below();

         for (Direction direction : Direction.Plane.HORIZONTAL) {
            BlockState blockState = level.getBlockState(below.relative(direction));
            FluidState fluidState = level.getFluidState(below.relative(direction));
            if (fluidState.is(FluidTags.SUPPORTS_SUGAR_CANE_ADJACENTLY)
               || blockState.is(BlockTags.SUPPORTS_SUGAR_CANE_ADJACENTLY)
               || state.canBeHydrated(level, pos, fluidState, below.relative(direction))) {
               return true;
            }
         }
      }

      return false;
   }

   @Override
   protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
      builder.add(AGE);
   }

   @Override
   public PlantType getPlantType(BlockGetter world, BlockPos pos) {
      return PlantType.BEACH;
   }

   @Override
   public BlockState getPlant(BlockGetter world, BlockPos pos) {
      return this.defaultBlockState();
   }
}
