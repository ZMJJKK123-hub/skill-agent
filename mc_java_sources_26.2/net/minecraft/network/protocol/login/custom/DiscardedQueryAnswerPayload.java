package net.minecraft.network.protocol.login.custom;

import java.util.function.Consumer;
import javax.annotation.Nullable;
import net.minecraft.network.FriendlyByteBuf;

public record DiscardedQueryAnswerPayload(@Nullable FriendlyByteBuf data, Consumer<FriendlyByteBuf> encoder) implements CustomQueryAnswerPayload {
   public static final DiscardedQueryAnswerPayload INSTANCE = new DiscardedQueryAnswerPayload();

   public DiscardedQueryAnswerPayload() {
      this(null, buf -> {});
   }

   @Override
   public void write(FriendlyByteBuf output) {
      if (this.data != null) {
         output.writeBytes(this.data.slice());
      } else {
         this.encoder.accept(output);
      }
   }
}
