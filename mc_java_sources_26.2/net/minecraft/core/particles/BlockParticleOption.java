package net.minecraft.core.particles;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

public class BlockParticleOption implements ParticleOptions {
   private static final Codec<BlockState> BLOCK_STATE_CODEC = Codec.withAlternative(
      BlockState.CODEC, BuiltInRegistries.BLOCK.byNameCodec(), Block::defaultBlockState
   );
   private final ParticleType<BlockParticleOption> type;
   private final BlockState state;
   private BlockPos pos;

   public static MapCodec<BlockParticleOption> codec(ParticleType<BlockParticleOption> type) {
      return BLOCK_STATE_CODEC.xmap(state -> new BlockParticleOption(type, state), o -> o.state).fieldOf("block_state");
   }

   public static StreamCodec<? super RegistryFriendlyByteBuf, BlockParticleOption> streamCodec(ParticleType<BlockParticleOption> type) {
      return ByteBufCodecs.idMapper(Block.BLOCK_STATE_REGISTRY).map(state -> new BlockParticleOption(type, state), o -> o.state);
   }

   public BlockParticleOption(ParticleType<BlockParticleOption> type, BlockState state) {
      this.type = type;
      this.state = state;
   }

   @Override
   public ParticleType<BlockParticleOption> getType() {
      return this.type;
   }

   public BlockState getState() {
      return this.state;
   }

   public BlockParticleOption setPos(BlockPos pos) {
      this.pos = pos;
      return this;
   }

   public BlockPos getPos() {
      return this.pos;
   }
}
