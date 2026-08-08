package net.minecraft.world.level.block;

import java.util.List;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.state.BlockState;

public interface BonemealableBlock {
   boolean isValidBonemealTarget(LevelReader var1, BlockPos var2, BlockState var3);

   boolean isBonemealSuccess(Level var1, RandomSource var2, BlockPos var3, BlockState var4);

   void performBonemeal(ServerLevel var1, RandomSource var2, BlockPos var3, BlockState var4);

   static boolean hasSpreadableNeighbourPos(LevelReader level, BlockPos pos, BlockState blockToPlace) {
      return getSpreadableNeighbourPos(Direction.Plane.HORIZONTAL.stream().toList(), level, pos, blockToPlace).isPresent();
   }

   static Optional<BlockPos> findSpreadableNeighbourPos(Level level, BlockPos pos, BlockState blockToPlace) {
      return getSpreadableNeighbourPos(Direction.Plane.HORIZONTAL.shuffledCopy(level.getRandom()), level, pos, blockToPlace);
   }

   private static Optional<BlockPos> getSpreadableNeighbourPos(List<Direction> directions, LevelReader level, BlockPos pos, BlockState blockToPlace) {
      for (Direction direction : directions) {
         BlockPos neighbourPos = pos.relative(direction);
         if (level.isEmptyBlock(neighbourPos) && blockToPlace.canSurvive(level, neighbourPos)) {
            return Optional.of(neighbourPos);
         }
      }

      return Optional.empty();
   }

   default BlockPos getParticlePos(BlockPos blockPos) {
      return switch (this.getType()) {
         case NEIGHBOR_SPREADER -> blockPos.above();
         case GROWER -> blockPos;
      };
   }

   default BonemealableBlock.Type getType() {
      return BonemealableBlock.Type.GROWER;
   }

   enum Type {
      NEIGHBOR_SPREADER,
      GROWER;
   }
}
