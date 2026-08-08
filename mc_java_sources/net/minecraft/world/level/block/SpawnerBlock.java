package net.minecraft.world.level.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.BlockEntityTypes;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import org.jspecify.annotations.Nullable;

public class SpawnerBlock extends BaseEntityBlock {
   public static final MapCodec<SpawnerBlock> CODEC = simpleCodec(SpawnerBlock::new);

   @Override
   public MapCodec<SpawnerBlock> codec() {
      return CODEC;
   }

   public SpawnerBlock(BlockBehaviour.Properties properties) {
      super(properties);
   }

   @Override
   public BlockEntity newBlockEntity(BlockPos worldPosition, BlockState blockState) {
      return new SpawnerBlockEntity(worldPosition, blockState);
   }

   @Override
   public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState blockState, BlockEntityType<T> type) {
      return createTickerHelper(type, BlockEntityTypes.MOB_SPAWNER, level.isClientSide() ? SpawnerBlockEntity::clientTick : SpawnerBlockEntity::serverTick);
   }

   @Override
   protected void spawnAfterBreak(BlockState state, ServerLevel level, BlockPos pos, ItemStack tool, boolean dropExperience) {
      super.spawnAfterBreak(state, level, pos, tool, dropExperience);
   }

   @Override
   public int getExpDrop(BlockState state, LevelReader level, RandomSource randomSource, BlockPos pos, int fortuneLevel, int silkTouchLevel) {
      return 15 + randomSource.nextInt(15) + randomSource.nextInt(15);
   }
}
