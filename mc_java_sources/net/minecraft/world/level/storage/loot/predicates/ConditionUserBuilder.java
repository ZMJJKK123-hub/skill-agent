package net.minecraft.world.level.storage.loot.predicates;

import java.util.function.Function;

public interface ConditionUserBuilder<T extends ConditionUserBuilder<T>> {
   T when(LootItemCondition.Builder var1);

   default <E> T when(Iterable<E> collection, Function<E, LootItemCondition.Builder> conditionProvider) {
      T result = this.unwrap();

      for (E value : collection) {
         result = result.when(conditionProvider.apply(value));
      }

      return result;
   }

   T unwrap();
}
