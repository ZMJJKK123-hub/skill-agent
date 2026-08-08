package net.minecraft.nbt;

import java.io.DataInput;
import java.io.IOException;

public interface TagType<T extends Tag> {
   T load(DataInput var1, NbtAccounter var2) throws IOException;

   StreamTagVisitor.ValueResult parse(DataInput var1, StreamTagVisitor var2, NbtAccounter var3) throws IOException;

   default void parseRoot(DataInput input, StreamTagVisitor output, NbtAccounter accounter) throws IOException {
      switch (output.visitRootEntry(this)) {
         case CONTINUE:
            this.parse(input, output, accounter);
         case HALT:
         default:
            break;
         case BREAK:
            this.skip(input, accounter);
      }
   }

   void skip(DataInput var1, int var2, NbtAccounter var3) throws IOException;

   void skip(DataInput var1, NbtAccounter var2) throws IOException;

   String getName();

   String getPrettyName();

   static TagType<EndTag> createInvalid(final int id) {
      return new TagType<EndTag>() {
         private IOException createException() {
            return new IOException("Invalid tag id: " + id);
         }

         public EndTag load(DataInput input, NbtAccounter accounter) throws IOException {
            throw this.createException();
         }

         @Override
         public StreamTagVisitor.ValueResult parse(DataInput input, StreamTagVisitor output, NbtAccounter accounter) throws IOException {
            throw this.createException();
         }

         @Override
         public void skip(DataInput input, int count, NbtAccounter accounter) throws IOException {
            throw this.createException();
         }

         @Override
         public void skip(DataInput input, NbtAccounter accounter) throws IOException {
            throw this.createException();
         }

         @Override
         public String getName() {
            return "INVALID[" + id + "]";
         }

         @Override
         public String getPrettyName() {
            return "UNKNOWN_" + id;
         }
      };
   }

   interface StaticSize<T extends Tag> extends TagType<T> {
      @Override
      default void skip(DataInput input, NbtAccounter accounter) throws IOException {
         input.skipBytes(this.size());
      }

      @Override
      default void skip(DataInput input, int count, NbtAccounter accounter) throws IOException {
         input.skipBytes(this.size() * count);
      }

      int size();
   }

   interface VariableSize<T extends Tag> extends TagType<T> {
      @Override
      default void skip(DataInput input, int count, NbtAccounter accounter) throws IOException {
         for (int i = 0; i < count; i++) {
            this.skip(input, accounter);
         }
      }
   }
}
