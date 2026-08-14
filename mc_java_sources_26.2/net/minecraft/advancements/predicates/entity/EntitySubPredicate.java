package net.minecraft.advancements.predicates.entity;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

public interface EntitySubPredicate {
   EntitySubPredicate ALWAYS_TRUE = (var0, var1, var2) -> true;

   boolean matches(Entity var1, ServerLevel var2, @Nullable Vec3 var3);

   default EntitySubPredicate and(EntitySubPredicate other) {
      return (entity, level, position) -> this.matches(entity, level, position) && other.matches(entity, level, position);
   }
}
