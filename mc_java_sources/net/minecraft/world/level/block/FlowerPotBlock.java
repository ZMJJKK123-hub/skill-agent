package net.minecraft.world.level.block;

import com.google.common.collect.Maps;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.Collections;
import java.util.Map;
import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ScheduledTickAccess;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.Nullable;

public class FlowerPotBlock extends Block {
   public static final MapCodec<FlowerPotBlock> CODEC = RecordCodecBuilder.mapCodec(
      i -> i.group(BuiltInRegistries.BLOCK.byNameCodec().fieldOf("potted").forGetter(b -> b.potted), propertiesCodec()).apply(i, FlowerPotBlock::new)
   );
   private static final Map<Block, Block> POTTED_BY_CONTENT = Maps.newHashMap();
   private static final VoxelShape SHAPE = Block.column(6.0, 0.0, 6.0);
   private final Block potted = null;
   private final Map<Identifier, Supplier<? extends Block>> fullPots;
   private final Supplier<FlowerPotBlock> emptyPot;
   private final Supplier<? extends Block> flowerDelegate;

   @Override
   public MapCodec<FlowerPotBlock> codec() {
      return CODEC;
   }

   public FlowerPotBlock(Block potted, BlockBehaviour.Properties properties) {
      this(
         Blocks.FLOWER_POT == null ? null : () -> (FlowerPotBlock)ForgeRegistries.BLOCKS.getDelegateOrThrow(Blocks.FLOWER_POT).get(),
         () -> ForgeRegistries.BLOCKS.getDelegateOrThrow(potted).get(),
         properties
      );
      if (Blocks.FLOWER_POT != null) {
         ((FlowerPotBlock)Blocks.FLOWER_POT).addPlant(ForgeRegistries.BLOCKS.getKey(potted), () -> this);
      }
   }

   public FlowerPotBlock(@Nullable Supplier<FlowerPotBlock> emptyPot, Supplier<? extends Block> p_53528_, BlockBehaviour.Properties properties) {
      super(properties);
      this.flowerDelegate = p_53528_;
      if (emptyPot == null) {
         this.fullPots = Maps.newHashMap();
         this.emptyPot = null;
      } else {
         this.fullPots = Collections.emptyMap();
         this.emptyPot = emptyPot;
      }
   }

   @Override
   protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
      return SHAPE;
   }

   @Override
   protected InteractionResult useItemOn(
      ItemStack itemStack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hitResult
   ) {
      BlockState newContents = (itemStack.getItem() instanceof BlockItem blockItem
            ? this.getEmptyPot()
               .fullPots
               .getOrDefault(ForgeRegistries.BLOCKS.getKey(blockItem.getBlock()), ForgeRegistries.BLOCKS.getDelegateOrThrow(Blocks.AIR))
               .get()
            : Blocks.AIR)
         .defaultBlockState();
      if (newContents.isAir()) {
         return InteractionResult.TRY_WITH_EMPTY_HAND;
      }

      if (!this.isEmpty()) {
         return InteractionResult.CONSUME;
      }

      level.setBlock(pos, newContents, 3);
      level.gameEvent(player, GameEvent.BLOCK_CHANGE, pos);
      player.awardStat(Stats.POT_FLOWER);
      itemStack.consume(1, player);
      return InteractionResult.SUCCESS;
   }

   @Override
   protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hitResult) {
      if (this.isEmpty()) {
         return InteractionResult.CONSUME;
      }

      ItemStack plant = new ItemStack(this.potted);
      if (!player.addItem(plant)) {
         player.drop(plant, false);
      }

      level.setBlock(pos, this.getEmptyPot().defaultBlockState(), 3);
      level.gameEvent(player, GameEvent.BLOCK_CHANGE, pos);
      return InteractionResult.SUCCESS;
   }

   @Override
   protected ItemStack getCloneItemStack(LevelReader level, BlockPos pos, BlockState state, boolean includeData) {
      return this.isEmpty() ? super.getCloneItemStack(level, pos, state, includeData) : new ItemStack(this.potted);
   }

   private boolean isEmpty() {
      return this.potted == Blocks.AIR;
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
      return directionToNeighbour == Direction.DOWN && !state.canSurvive(level, pos)
         ? Blocks.AIR.defaultBlockState()
         : super.updateShape(state, level, ticks, pos, directionToNeighbour, neighbourPos, neighbourState, random);
   }

   public Block getPotted() {
      return this.flowerDelegate.get();
   }

   @Override
   protected boolean isPathfindable(BlockState state, PathComputationType type) {
      return false;
   }

   @Override
   protected boolean isRandomlyTicking(BlockState state) {
      return state.is(Blocks.POTTED_OPEN_EYEBLOSSOM) || state.is(Blocks.POTTED_CLOSED_EYEBLOSSOM);
   }

   @Override
   protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
      if (this.isRandomlyTicking(state)) {
         boolean isOpen = this.potted == Blocks.OPEN_EYEBLOSSOM;
         boolean shouldBeOpen = level.environmentAttributes().getValue(EnvironmentAttributes.EYEBLOSSOM_OPEN, pos).toBoolean(isOpen);
         if (isOpen != shouldBeOpen) {
            level.setBlock(pos, this.opposite(state), 3);
            EyeblossomBlock.Type newType = EyeblossomBlock.Type.fromBoolean(isOpen).transform();
            newType.spawnTransformParticle(level, pos, random);
            level.playSound(null, pos, newType.longSwitchSound(), SoundSource.BLOCKS, 1.0F, 1.0F);
         }
      }

      super.randomTick(state, level, pos, random);
   }

   public BlockState opposite(BlockState state) {
      if (state.is(Blocks.POTTED_OPEN_EYEBLOSSOM)) {
         return Blocks.POTTED_CLOSED_EYEBLOSSOM.defaultBlockState();
      } else {
         return state.is(Blocks.POTTED_CLOSED_EYEBLOSSOM) ? Blocks.POTTED_OPEN_EYEBLOSSOM.defaultBlockState() : state;
      }
   }

   public FlowerPotBlock getEmptyPot() {
      return this.emptyPot == null ? this : this.emptyPot.get();
   }

   public void addPlant(Identifier flower, Supplier<? extends Block> fullPot) {
      if (this.getEmptyPot() != this) {
         throw new IllegalArgumentException("Cannot add plant to non-empty pot: " + this);
      }

      this.fullPots.put(flower, fullPot);
   }

   public Map<Identifier, Supplier<? extends Block>> getFullPotsView() {
      return Collections.unmodifiableMap(this.fullPots);
   }
}
