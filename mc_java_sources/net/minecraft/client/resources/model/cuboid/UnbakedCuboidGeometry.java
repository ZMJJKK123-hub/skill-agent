package net.minecraft.client.resources.model.cuboid;

import java.util.List;
import java.util.Map.Entry;
import java.util.function.Function;
import net.minecraft.client.renderer.block.dispatch.ModelState;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ModelDebugName;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.geometry.QuadCollection;
import net.minecraft.client.resources.model.geometry.UnbakedGeometry;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.client.resources.model.sprite.TextureSlots;
import net.minecraft.core.Direction;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3fc;

@OnlyIn(Dist.CLIENT)
public record UnbakedCuboidGeometry(List<CuboidModelElement> elements) implements UnbakedGeometry {
   @Override
   public QuadCollection bake(TextureSlots textures, ModelBaker modelBaker, ModelState modelState, ModelDebugName name) {
      return bake(this.elements, textures, modelBaker, modelState, name);
   }

   public static QuadCollection bake(
      List<CuboidModelElement> elements, TextureSlots textures, ModelBaker modelBaker, ModelState modelState, ModelDebugName name
   ) {
      QuadCollection.Builder builder = new QuadCollection.Builder();
      bake(builder, elements, textures, modelBaker, modelState, name, id -> modelBaker.materials().resolveSlot(textures, id, name));
      return builder.build();
   }

   public static void bake(
      QuadCollection.Builder builder,
      List<CuboidModelElement> elements,
      TextureSlots textures,
      ModelBaker modelBaker,
      ModelState modelState,
      ModelDebugName name,
      Function<String, Material.Baked> materialMapper
   ) {
      for (CuboidModelElement element : elements) {
         boolean drawXFaces = true;
         boolean drawYFaces = true;
         boolean drawZFaces = true;
         Vector3fc from = element.from();
         Vector3fc to = element.to();
         if (from.x() == to.x()) {
            drawYFaces = false;
            drawZFaces = false;
         }

         if (from.y() == to.y()) {
            drawXFaces = false;
            drawZFaces = false;
         }

         if (from.z() == to.z()) {
            drawXFaces = false;
            drawYFaces = false;
         }

         if (drawXFaces || drawYFaces || drawZFaces) {
            for (Entry<Direction, CuboidFace> entry : element.faces().entrySet()) {
               Direction facing = entry.getKey();
               CuboidFace face = entry.getValue();

               boolean shouldDrawFace = switch (facing.getAxis()) {
                  case X -> drawXFaces;
                  case Y -> drawYFaces;
                  case Z -> drawZFaces;
               };
               if (shouldDrawFace) {
                  Material.Baked material = materialMapper.apply(face.texture());
                  BakedQuad quad = FaceBakery.bakeQuad(
                     modelBaker, from, to, face, material, facing, modelState, element.rotation(), element.shade(), element.lightEmission()
                  );
                  if (face.cullForDirection() == null) {
                     builder.addUnculledFace(quad);
                  } else {
                     builder.addCulledFace(Direction.rotate(modelState.transformation().getMatrix(), face.cullForDirection()), quad);
                  }
               }
            }
         }
      }
   }
}
