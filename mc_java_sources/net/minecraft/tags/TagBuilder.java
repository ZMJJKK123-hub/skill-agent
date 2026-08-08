package net.minecraft.tags;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;
import net.minecraft.resources.Identifier;
import net.minecraftforge.common.extensions.IForgeRawTagBuilder;

public class TagBuilder implements IForgeRawTagBuilder {
   private final List<TagEntry> entries = new ArrayList<>();
   private boolean replace = false;
   private final List<TagEntry> removeEntries = new ArrayList<>();

   public static TagBuilder create() {
      return new TagBuilder();
   }

   public List<TagEntry> build() {
      return List.copyOf(this.entries);
   }

   public boolean shouldReplace() {
      return this.replace;
   }

   public TagBuilder setReplace(boolean replace) {
      this.replace = replace;
      return this;
   }

   public TagBuilder add(TagEntry entry) {
      this.entries.add(entry);
      return this;
   }

   public TagBuilder addElement(Identifier id) {
      return this.add(TagEntry.element(id));
   }

   public TagBuilder addOptionalElement(Identifier id) {
      return this.add(TagEntry.optionalElement(id));
   }

   public TagBuilder addTag(Identifier id) {
      return this.add(TagEntry.tag(id));
   }

   public TagBuilder addOptionalTag(Identifier id) {
      return this.add(TagEntry.optionalTag(id));
   }

   public Stream<TagEntry> getRemoveEntries() {
      return this.removeEntries.stream();
   }

   public TagBuilder remove(TagEntry entry) {
      this.removeEntries.add(entry);
      return this;
   }
}
