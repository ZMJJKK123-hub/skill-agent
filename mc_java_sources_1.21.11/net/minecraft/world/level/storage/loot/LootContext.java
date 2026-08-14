package net.minecraft.world.level.storage.loot;

import com.google.common.collect.Sets;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import net.minecraft.core.HolderGetter;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.util.StringRepresentable;
import net.minecraft.util.context.ContextKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.storage.loot.functions.LootItemFunction;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import org.jspecify.annotations.Nullable;

public class LootContext {
    private final LootParams params;
    private final RandomSource random;
    private final HolderGetter.Provider lootDataResolver;
    private final Set<LootContext.VisitedEntry<?>> visitedElements = Sets.newLinkedHashSet();
    private Identifier queriedLootTableId;

    LootContext(LootParams p_287722_, RandomSource p_287702_, HolderGetter.Provider p_330439_) {
        this(p_287722_, p_287702_, p_330439_, null);
    }

    LootContext(LootParams p_287722_, RandomSource p_287702_, HolderGetter.Provider p_330439_, Identifier queriedLootTableId) {
        this.params = p_287722_;
        this.random = p_287702_;
        this.lootDataResolver = p_330439_;
        this.queriedLootTableId = queriedLootTableId;
    }

    public boolean hasParameter(ContextKey<?> p_368930_) {
        return this.params.contextMap().has(p_368930_);
    }

    public <T> T getParameter(ContextKey<T> p_363450_) {
        return this.params.contextMap().getOrThrow(p_363450_);
    }

    public <T> @Nullable T getOptionalParameter(ContextKey<T> p_368704_) {
        return this.params.contextMap().getOptional(p_368704_);
    }

    public void addDynamicDrops(Identifier p_458292_, Consumer<ItemStack> p_78944_) {
        this.params.addDynamicDrops(p_458292_, p_78944_);
    }

    public boolean hasVisitedElement(LootContext.VisitedEntry<?> p_279182_) {
        return this.visitedElements.contains(p_279182_);
    }

    public boolean pushVisitedElement(LootContext.VisitedEntry<?> p_279152_) {
        return this.visitedElements.add(p_279152_);
    }

    public void popVisitedElement(LootContext.VisitedEntry<?> p_279198_) {
        this.visitedElements.remove(p_279198_);
    }

    public HolderGetter.Provider getResolver() {
        return this.lootDataResolver;
    }

    public RandomSource getRandom() {
        return this.random;
    }

    public float getLuck() {
        return this.params.getLuck();
    }

    public ServerLevel getLevel() {
        return this.params.getLevel();
    }

    public LootParams getParams() {
        return this.params;
    }

    public static LootContext.VisitedEntry<LootTable> createVisitedEntry(LootTable p_279327_) {
        return new LootContext.VisitedEntry<>(LootDataType.TABLE, p_279327_);
    }

    public static LootContext.VisitedEntry<LootItemCondition> createVisitedEntry(LootItemCondition p_279250_) {
        return new LootContext.VisitedEntry<>(LootDataType.PREDICATE, p_279250_);
    }

    public static LootContext.VisitedEntry<LootItemFunction> createVisitedEntry(LootItemFunction p_279163_) {
        return new LootContext.VisitedEntry<>(LootDataType.MODIFIER, p_279163_);
    }

    public int getLootingModifier() {
        return net.minecraftforge.common.ForgeHooks.getLootingLevel(getOptionalParameter(LootContextParams.THIS_ENTITY), getOptionalParameter(LootContextParams.ATTACKING_ENTITY), getOptionalParameter(LootContextParams.DAMAGE_SOURCE));
    }

    public void setQueriedLootTableId(Identifier queriedLootTableId) {
        if (this.queriedLootTableId == null && queriedLootTableId != null) this.queriedLootTableId = queriedLootTableId;
    }

    public Identifier getQueriedLootTableId() {
        return this.queriedLootTableId == null ? net.minecraftforge.common.loot.LootTableIdCondition.UNKNOWN_LOOT_TABLE : this.queriedLootTableId;
    }

    public static enum BlockEntityTarget implements StringRepresentable, LootContextArg.SimpleGetter<BlockEntity> {
        BLOCK_ENTITY("block_entity", LootContextParams.BLOCK_ENTITY);

        private final String name;
        private final ContextKey<? extends BlockEntity> param;

        private BlockEntityTarget(final String p_425102_, final ContextKey<? extends BlockEntity> p_425125_) {
            this.name = p_425102_;
            this.param = p_425125_;
        }

        @Override
        public ContextKey<? extends BlockEntity> contextParam() {
            return this.param;
        }

        @Override
        public String getSerializedName() {
            return this.name;
        }
    }

    public static class Builder {
        private final LootParams params;
        private @Nullable RandomSource random;
        private Identifier queriedLootTableId; // Forge: correctly pass around loot table ID with copy constructor

        public Builder(LootParams p_287628_) {
            this.params = p_287628_;
        }

        public Builder(LootContext context) {
            this.params = context.params;
            this.random = context.random;
            this.queriedLootTableId = context.queriedLootTableId;
        }

        public LootContext.Builder withOptionalRandomSeed(long p_78966_) {
            if (p_78966_ != 0L) {
                this.random = RandomSource.create(p_78966_);
            }

            return this;
        }

        public LootContext.Builder withOptionalRandomSource(RandomSource p_345173_) {
            this.random = p_345173_;
            return this;
        }

        public LootContext.Builder withQueriedLootTableId(Identifier queriedLootTableId) {
            this.queriedLootTableId = queriedLootTableId;
            return this;
        }

        public ServerLevel getLevel() {
            return this.params.getLevel();
        }

        public LootContext create(Optional<Identifier> p_299315_) {
            ServerLevel serverlevel = this.getLevel();
            MinecraftServer minecraftserver = serverlevel.getServer();
            RandomSource randomsource = Optional.ofNullable(this.random).or(() -> p_299315_.map(serverlevel::getRandomSequence)).orElseGet(serverlevel::getRandom);
            return new LootContext(this.params, randomsource, minecraftserver.reloadableRegistries().lookup(), queriedLootTableId);
        }
    }

    public static enum EntityTarget implements StringRepresentable, LootContextArg.SimpleGetter<Entity> {
        THIS("this", LootContextParams.THIS_ENTITY),
        ATTACKER("attacker", LootContextParams.ATTACKING_ENTITY),
        DIRECT_ATTACKER("direct_attacker", LootContextParams.DIRECT_ATTACKING_ENTITY),
        ATTACKING_PLAYER("attacking_player", LootContextParams.LAST_DAMAGE_PLAYER),
        TARGET_ENTITY("target_entity", LootContextParams.TARGET_ENTITY),
        INTERACTING_ENTITY("interacting_entity", LootContextParams.INTERACTING_ENTITY);

        public static final StringRepresentable.EnumCodec<LootContext.EntityTarget> CODEC = StringRepresentable.fromEnum(LootContext.EntityTarget::values);
        private final String name;
        private final ContextKey<? extends Entity> param;

        private EntityTarget(final String p_79001_, final ContextKey<? extends Entity> p_361944_) {
            this.name = p_79001_;
            this.param = p_361944_;
        }

        @Override
        public ContextKey<? extends Entity> contextParam() {
            return this.param;
        }

        public static LootContext.EntityTarget getByName(String p_79007_) {
            LootContext.EntityTarget lootcontext$entitytarget = CODEC.byName(p_79007_);
            if (lootcontext$entitytarget != null) {
                return lootcontext$entitytarget;
            } else {
                throw new IllegalArgumentException("Invalid entity target " + p_79007_);
            }
        }

        @Override
        public String getSerializedName() {
            return this.name;
        }
    }

    public static enum ItemStackTarget implements StringRepresentable, LootContextArg.SimpleGetter<ItemStack> {
        TOOL("tool", LootContextParams.TOOL);

        private final String name;
        private final ContextKey<? extends ItemStack> param;

        private ItemStackTarget(final String p_429623_, final ContextKey<? extends ItemStack> p_422507_) {
            this.name = p_429623_;
            this.param = p_422507_;
        }

        @Override
        public ContextKey<? extends ItemStack> contextParam() {
            return this.param;
        }

        @Override
        public String getSerializedName() {
            return this.name;
        }
    }

    public record VisitedEntry<T>(LootDataType<T> type, T value) {
    }
}
