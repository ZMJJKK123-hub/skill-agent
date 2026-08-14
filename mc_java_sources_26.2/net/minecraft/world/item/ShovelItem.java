package net.minecraft.world.item;

import com.google.common.collect.Maps;
import com.google.common.collect.ImmutableMap.Builder;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraftforge.common.ToolAction;
import net.minecraftforge.common.ToolActions;
import org.jetbrains.annotations.Nullable;

public class ShovelItem extends Item {
   protected static final Map<Block, BlockState> FLATTENABLES = Maps.newHashMap(
      new Builder()
         .put(Blocks.GRASS_BLOCK, Blocks.DIRT_PATH.defaultBlockState())
         .put(Blocks.DIRT, Blocks.DIRT_PATH.defaultBlockState())
         .put(Blocks.PODZOL, Blocks.DIRT_PATH.defaultBlockState())
         .put(Blocks.COARSE_DIRT, Blocks.DIRT_PATH.defaultBlockState())
         .put(Blocks.MYCELIUM, Blocks.DIRT_PATH.defaultBlockState())
         .put(Blocks.ROOTED_DIRT, Blocks.DIRT_PATH.defaultBlockState())
         .build()
   );

   public ShovelItem(ToolMaterial material, float attackDamageBaseline, float attackSpeedBaseline, Item.Properties properties) {
      super(properties.shovel(material, attackDamageBaseline, attackSpeedBaseline));
   }

   @Override
   public InteractionResult useOn(UseOnContext context) {
      Level level = context.getLevel();
      BlockPos pos = context.getClickedPos();
      BlockState blockState = level.getBlockState(pos);
      if (context.getClickedFace() == Direction.DOWN) {
         return InteractionResult.PASS;
      }

      Player player = context.getPlayer();
      BlockState newState = blockState.getToolModifiedState(context, ToolActions.SHOVEL_FLATTEN, false);
      BlockState updatedState = null;
      if (newState != null && level.isEmptyBlock(pos.above())) {
         level.playSound(player, pos, SoundEvents.SHOVEL_FLATTEN, SoundSource.BLOCKS, 1.0F, 1.0F);
         updatedState = newState;
      } else if (blockState.getBlock() instanceof CampfireBlock && blockState.getValue(CampfireBlock.LIT)) {
         if (!level.isClientSide()) {
            level.levelEvent(null, 1009, pos, 0);
         }

         CampfireBlock.dowse(context.getPlayer(), level, pos, blockState);
         updatedState = blockState.setValue(CampfireBlock.LIT, false);
      }

      if (updatedState != null) {
         if (!level.isClientSide()) {
            level.setBlock(pos, updatedState, 11);
            level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, updatedState));
            if (player != null) {
               context.getItemInHand().hurtAndBreak(1, player, context.getHand().asEquipmentSlot());
            }
         }

         return InteractionResult.SUCCESS;
      } else {
         return InteractionResult.PASS;
      }
   }

   @Nullable
   public static BlockState getShovelPathingState(BlockState originalState) {
      return FLATTENABLES.get(originalState.getBlock());
   }

   @Override
   public boolean canPerformAction(ItemStack stack, ToolAction toolAction) {
      return ToolActions.DEFAULT_SHOVEL_ACTIONS.contains(toolAction);
   }
}
