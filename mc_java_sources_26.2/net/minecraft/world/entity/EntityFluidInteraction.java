package net.minecraft.world.entity;

import it.unimi.dsi.fastutil.objects.Reference2ObjectArrayMap;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Map.Entry;
import java.util.function.BiPredicate;
import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.ForgeMod;
import net.minecraftforge.fluids.FluidType;
import org.jspecify.annotations.Nullable;

public class EntityFluidInteraction {
   private static final Map<TagKey<Fluid>, Supplier<? extends EntityFluidInteraction.Tracker>> MODDED_TYPES = new HashMap<>();
   private final Map<TagKey<Fluid>, EntityFluidInteraction.Tracker> trackerByFluid = new Reference2ObjectArrayMap();
   private final Map<FluidType, EntityFluidInteraction.Tracker> trackerByFluidType = new Reference2ObjectArrayMap();
   private boolean isInFluid = false;
   private FluidType eyeFluid = ForgeMod.EMPTY_TYPE.get();
   private final EntityFluidInteraction.Tracker[] NONE = new EntityFluidInteraction.Tracker[0];

   public static void register(TagKey<Fluid> fluid) {
      register(fluid, EntityFluidInteraction.Tracker::new);
   }

   public static void register(TagKey<Fluid> fluid, Supplier<? extends EntityFluidInteraction.Tracker> factory) {
      register(fluid, factory);
   }

   public EntityFluidInteraction(Set<TagKey<Fluid>> fluids) {
      for (TagKey<Fluid> fluid : fluids) {
         this.trackerByFluid.put(fluid, new EntityFluidInteraction.Tracker());
      }

      for (Entry<TagKey<Fluid>, Supplier<? extends EntityFluidInteraction.Tracker>> entry : MODDED_TYPES.entrySet()) {
         if (!fluids.contains(entry.getKey())) {
            this.trackerByFluid.put(entry.getKey(), entry.getValue().get());
         }
      }
   }

   public EntityFluidInteraction.@Nullable Tracker getTracker(TagKey<Fluid> fluid) {
      return this.trackerByFluid.get(fluid);
   }

   public void update(Entity entity, boolean ignoreCurrent) {
      this.trackerByFluid.values().forEach(EntityFluidInteraction.Tracker::reset);
      this.trackerByFluidType.values().forEach(EntityFluidInteraction.Tracker::reset);
      this.isInFluid = false;
      this.eyeFluid = ForgeMod.EMPTY_TYPE.get();
      AABB box = entity.getFluidInteractionBox();
      if (box != null) {
         int x0 = Mth.floor(box.minX);
         int y0 = Mth.floor(box.minY);
         int z0 = Mth.floor(box.minZ);
         int x1 = Mth.ceil(box.maxX) - 1;
         int y1 = Mth.ceil(box.maxY) - 1;
         int z1 = Mth.ceil(box.maxZ) - 1;
         if (hasFluidAndLoaded(entity.level(), x0 - 1, y0, z0 - 1, x1 + 1, y1, z1 + 1)) {
            double entityY = entity.getBoundingBox().minY;
            int eyeBlockX = entity.getBlockX();
            double eyeY = entity.getEyeY();
            int eyeBlockZ = entity.getBlockZ();
            Fluid lastFluidType = null;
            EntityFluidInteraction.Tracker[] trackers = null;
            BlockGetter level = entity.level();
            BlockPos.MutableBlockPos mutablePos = new BlockPos.MutableBlockPos();

            for (int x = x0; x <= x1; x++) {
               for (int y = y0; y <= y1; y++) {
                  for (int z = z0; z <= z1; z++) {
                     mutablePos.set(x, y, z);
                     FluidState fluidState = level.getFluidState(mutablePos);
                     if (!fluidState.isEmpty()) {
                        this.isInFluid = true;
                        double fluidBottom = mutablePos.getY();
                        double fluidTop = fluidBottom + fluidState.getHeight(level, mutablePos);
                        if (!(fluidTop < box.minY)) {
                           Fluid fluidType = fluidState.getType();
                           if (fluidType != lastFluidType) {
                              lastFluidType = fluidType;
                              trackers = this.getTrackersFor(fluidType);
                           }

                           for (EntityFluidInteraction.Tracker tracker : trackers) {
                              if (x == eyeBlockX && z == eyeBlockZ && eyeY >= fluidBottom && eyeY <= fluidTop) {
                                 tracker.eyesInside = true;
                                 this.eyeFluid = lastFluidType.getFluidType();
                              }

                              tracker.height = Math.max(fluidTop - entityY, tracker.height);
                              if (!ignoreCurrent || !fluidState.getType().getFluidType().canPushEntity(entity)) {
                                 Vec3 flow = fluidState.getFlow(level, mutablePos, entity);
                                 if (tracker.height < 0.4) {
                                    flow = flow.scale(tracker.height);
                                 }

                                 tracker.accumulateCurrent(flow);
                              }
                           }
                        }
                     }
                  }
               }
            }
         }
      }
   }

   private static boolean hasFluidAndLoaded(Level level, int x0, int y0, int z0, int x1, int y1, int z1) {
      int sectionX0 = SectionPos.blockToSectionCoord(x0);
      int sectionY0 = SectionPos.blockToSectionCoord(y0);
      int sectionZ0 = SectionPos.blockToSectionCoord(z0);
      int sectionX1 = SectionPos.blockToSectionCoord(x1);
      int sectionY1 = SectionPos.blockToSectionCoord(y1);
      int sectionZ1 = SectionPos.blockToSectionCoord(z1);
      boolean hasFluid = false;

      for (int chunkZ = sectionZ0; chunkZ <= sectionZ1; chunkZ++) {
         for (int chunkX = sectionX0; chunkX <= sectionX1; chunkX++) {
            ChunkAccess chunk = level.getChunk(chunkX, chunkZ, ChunkStatus.FULL, false);
            if (chunk == null) {
               return false;
            }

            LevelChunkSection[] sections = chunk.getSections();

            for (int sectionY = sectionY0; sectionY <= sectionY1; sectionY++) {
               int sectionIndex = chunk.getSectionIndexFromSectionY(sectionY);
               if (sectionIndex >= 0 && sectionIndex < sections.length) {
                  hasFluid |= sections[sectionIndex].hasFluid();
               }
            }
         }
      }

      return hasFluid;
   }

   private EntityFluidInteraction.@Nullable Tracker[] getTrackersFor(Fluid fluid) {
      ArrayList<EntityFluidInteraction.Tracker> ret = new ArrayList<>(1);

      for (Entry<TagKey<Fluid>, EntityFluidInteraction.Tracker> entry : this.trackerByFluid.entrySet()) {
         TagKey<Fluid> tag = entry.getKey();
         if (fluid.is(tag)) {
            ret.add(entry.getValue());
         }
      }

      ret.add(this.trackerByFluidType.computeIfAbsent(fluid.getFluidType(), k -> new EntityFluidInteraction.Tracker()));
      return ret.isEmpty() ? this.NONE : ret.toArray(EntityFluidInteraction.Tracker[]::new);
   }

   public void applyCurrentTo(Entity entity) {
      for (Entry<FluidType, EntityFluidInteraction.Tracker> entry : this.trackerByFluidType.entrySet()) {
         if (entity.isPushedByFluid(entry.getKey())) {
            entry.getValue().applyCurrentTo(entity, entity.getFluidMotionScale(entry.getKey()));
         }
      }
   }

   public void applyCurrentTo(TagKey<Fluid> fluid, Entity entity, double scale) {
      EntityFluidInteraction.Tracker tracker = this.trackerByFluid.get(fluid);
      if (tracker != null) {
         tracker.applyCurrentTo(entity, scale);
      }
   }

   public double getFluidHeight(TagKey<Fluid> fluid) {
      EntityFluidInteraction.Tracker tracker = this.trackerByFluid.get(fluid);
      return tracker != null ? tracker.height : 0.0;
   }

   public double getFluidHeight(Fluid fluid) {
      return this.getFluidHeight(fluid.getFluidType());
   }

   public double getFluidHeight(FluidType fluid) {
      EntityFluidInteraction.Tracker tracker = this.trackerByFluidType.get(fluid);
      return tracker == null ? 0.0 : tracker.height;
   }

   public boolean isInFluid() {
      return this.isInFluid;
   }

   public boolean isInFluid(TagKey<Fluid> fluid) {
      return this.getFluidHeight(fluid) > 0.0;
   }

   public boolean isEyeInFluid(TagKey<Fluid> fluid) {
      EntityFluidInteraction.Tracker tracker = this.trackerByFluid.get(fluid);
      return tracker != null && tracker.eyesInside;
   }

   public boolean isEyeInFluid(Fluid fluid) {
      return this.isEyeInFluid(fluid.getFluidType());
   }

   public boolean isEyeInFluid(FluidType fluid) {
      EntityFluidInteraction.Tracker tracker = this.trackerByFluidType.get(fluid);
      return tracker != null && tracker.eyesInside;
   }

   public FluidType getEyeFluid() {
      return this.eyeFluid;
   }

   public FluidType getMaxHeightFluid() {
      FluidType ret = ForgeMod.EMPTY_TYPE.get();
      double height = 0.0;
      EntityFluidInteraction.Tracker max = null;

      for (Entry<FluidType, EntityFluidInteraction.Tracker> entry : this.trackerByFluidType.entrySet()) {
         if (entry.getValue().height > height) {
            height = entry.getValue().height;
            ret = entry.getKey();
         }
      }

      return ret;
   }

   public final boolean isInFluid(BiPredicate<FluidType, Double> predicate, boolean forAllTypes) {
      boolean match = false;

      for (Entry<FluidType, EntityFluidInteraction.Tracker> entry : this.trackerByFluidType.entrySet()) {
         if (entry.getValue().height > 0.0 && predicate.test(entry.getKey(), entry.getValue().height)) {
            match = true;
            if (!forAllTypes) {
               return true;
            }
         } else if (forAllTypes) {
            return false;
         }
      }

      return match;
   }

   private static class Tracker {
      private double height;
      private boolean eyesInside;
      private Vec3 accumulatedCurrent = Vec3.ZERO;
      private int currentCount;

      public void reset() {
         this.height = 0.0;
         this.eyesInside = false;
         this.accumulatedCurrent = Vec3.ZERO;
         this.currentCount = 0;
      }

      public void accumulateCurrent(Vec3 flow) {
         this.accumulatedCurrent = this.accumulatedCurrent.add(flow);
         this.currentCount++;
      }

      public void applyCurrentTo(Entity entity, double scale) {
         if (this.currentCount != 0 && !(this.accumulatedCurrent.lengthSqr() < 1.0E-5F)) {
            Vec3 impulse;
            if (!(entity instanceof Player)) {
               impulse = this.accumulatedCurrent.normalize();
            } else {
               impulse = this.accumulatedCurrent.scale(1.0 / this.currentCount);
            }

            Vec3 oldMovement = entity.getDeltaMovement();
            impulse = impulse.scale(scale);
            double min = 0.003;
            if (Math.abs(oldMovement.x) < 0.003 && Math.abs(oldMovement.z) < 0.003 && impulse.length() < 0.0045000000000000005) {
               impulse = impulse.normalize().scale(0.0045000000000000005);
            }

            entity.addDeltaMovement(impulse);
         }
      }
   }
}
