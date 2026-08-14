package net.minecraft.tags;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.resources.Identifier;

public class TagBuilder implements net.minecraftforge.common.extensions.IForgeRawTagBuilder {
    private final List<TagEntry> entries = new ArrayList<>();

    public static TagBuilder create() {
        return new TagBuilder();
    }

    public List<TagEntry> build() {
        return List.copyOf(this.entries);
    }

    public TagBuilder add(TagEntry p_215903_) {
        this.entries.add(p_215903_);
        return this;
    }

    public TagBuilder addElement(Identifier p_451128_) {
        return this.add(TagEntry.element(p_451128_));
    }

    public TagBuilder addOptionalElement(Identifier p_458467_) {
        return this.add(TagEntry.optionalElement(p_458467_));
    }

    public TagBuilder addTag(Identifier p_450703_) {
        return this.add(TagEntry.tag(p_450703_));
    }

    public TagBuilder addOptionalTag(Identifier p_458048_) {
        return this.add(TagEntry.optionalTag(p_458048_));
    }

    /** Forge: Used for datagen */
    private final List<TagEntry> removeEntries = new ArrayList<>();
    private boolean replace = false;

    public java.util.stream.Stream<TagEntry> getRemoveEntries() { // should this return the List instead? Might end up with mem leaks from unterminated streams otherwise -Paint_Ninja
        return this.removeEntries.stream();
    }

    /** Forge: Add an entry to be removed from this tag in datagen */
    public TagBuilder remove(TagEntry entry) {
        this.removeEntries.add(entry);
        return this;
    }

    /** Forge: Set the replace property of this tag */
    public TagBuilder replace(boolean value) {
        this.replace = value;
        return this;
    }

    /** Forge: Is this tag set to replace or not? */
    public boolean isReplace() {
        return this.replace;
    }
}
