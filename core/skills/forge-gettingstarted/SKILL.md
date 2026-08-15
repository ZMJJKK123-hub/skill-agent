---
name: forge-gettingstarted
description: Getting started with Forge modding: build.gradle, mod metadata, dependencies, javafml, @Mod.
whenToUse: Use when setting up a Forge mod project or build.gradle.
---

## ⚠️ Hard Facts About This Project's Environment (Must Not Be Violated)

The following are the deployed Forge build environment facts on this machine. **When a build fails, judge by this section first — do not use old Forge knowledge to conclude a version "does not exist".**

### Version Number Format (new scheme)
- This project's Forge dependency version format is `26.2-65.1.x`: **`26.2` is the Minecraft version number (new naming), `65.1.x` is the Forge build number**.
- This is a **valid modern version number**, not an "old format" or a "typo". Even though it looks like the `1.12`-era format, it is **forbidden** to judge it as "version does not exist".
- Old knowledge (e.g. `1.20.1`=47.x, `1.21`=52.x) **does not apply** to this project; do not "fix" build.gradle based on it.

### Locally Cached Versions (no online downloads)
The local Gradle cache already contains the following Forge versions (`C:\Users\59639\.gradle\caches\minecraftforge\forgegradle\mavenizer\caches\forge\net\minecraftforge\forge\`):
- `26.2-65.1.0` (base preinstalled version)
- `26.2-65.1.1` (version generated during the task)
- `1.21.8-58.0.3`

When using any version, **prefer the local cache**; **do not** query `maven.minecraftforge.net` online or try to download new versions.

### Build Failure Handling Rules
1. **Do not modify** the `minecraft.dependency('net.minecraftforge:forge:...')` version in `build.gradle`.
2. When Minecraft classes are missing (e.g. `ResourceLocation`, `SwordItem`), first check that the compile classpath includes the local `recompiled.jar` (see `compileOnly files(...)` in build.gradle), **rather than changing the version number**.
3. On `Could not resolve`, first check whether the local cache has that version; if yes use it directly, otherwise fall back to the version already configured in build.gradle.
4. Do not repeatedly rewrite build.gradle / settings.gradle because of one build error; first investigate dependency resolution and classpath issues.

---

Getting Started with Forge
==========================

If you have never made a Forge mod before, this section will provide the minimum amount of information needed to setup a Forge development environment. The rest of the documentation is about where to go from here.

Prerequisites
-------------

* An installation of the Java 21 Development Kit (JDK) and 64-bit Java Virtual Machine (JVM). Forge recommends and officially supports [Eclipse Temurin][jdk].
* Familiarity with an Integrated Development Environment (IDE).
    * It is recommended to use an IDE with Gradle integration.

From Zero to Modding
--------------------

1. Download the Mod Developer Kit (MDK) from the [Forge file site][files] by clicking 'Mdk' followed by the 'Skip' button in the top right after waiting for a period of time. It is recommended to download the latest version of Forge whenever possible.
1. Extract the downloaded MDK into an empty directory. This will be your mod's directory, which should now contain some gradle files and a `src` subdirectory containing the example mod.

    !!! note
        A number of files can be reused across different mods. These files are:

        * the `gradle` subdirectory
        * `build.gradle`
        * `gradlew`
        * `gradlew.bat`
        * `settings.gradle`

        The `src` subdirectory does not need to be copied across workspaces; however, you may need to refresh the Gradle project if the java (`src/main/java`) and resource (`src/main/resources`) are created later.

1. Open your selected IDE:
    * Forge only explicitly supports development on Eclipse and IntelliJ IDEA, but there are additional run configurations for Visual Studio Code. Regardless, any environment, from Apache NetBeans to Vim / Emacs, can be used.
    * Eclipse and IntelliJ IDEA's Gradle integration, both installed and enabled by default, will handle the rest of the initial workspace setup on import or open. This includes downloading the necessary packages from Mojang, MinecraftForge, etc. The 'Gradle for Java' plugin is needed for Visual Studio Code to do the same.
    * Gradle will need to be invoked to re-evaluate the project for almost all changes to its associated files (e.g., `build.gradle`, `settings.gradle`, etc.). Some IDEs come with 'Refresh' buttons to do this; however, it can be done through the terminal via `gradlew`.
1. Generate run configurations for your selected IDE:
    * **Eclipse**: Run the `genEclipseRuns` task.
    * **IntelliJ IDEA**: Run the `genIntellijRuns` task. If a "module not specified" error occurs, set the [`ideaModule` property][config] to your 'main' module (typically `${project.name}.main`).
    * **Visual Studio Code**: Run the `genVSCodeRuns` task.
    * **Other IDEs**: You can run the configurations directly using `gradle run*` (e.g., `runClient`, `runServer`, `runData`, `runGameTestServer`). These can also be used with the supported IDEs.

Customizing Your Mod Information
--------------------------------

Edit the `build.gradle` file to customize how your mod is built (e.g., file name, artifact version, etc.).

!!! important
    Do **not** edit the `settings.gradle` unless you know what you are doing. The file specifies the repository that [ForgeGradle] is uploaded to.

### Recommended `build.gradle` Customizations

#### Mod Id Replacement

Replace all occurrences of `examplemod`, including [`mods.toml` and the main mod file][modfiles] with the mod id of your mod. This also includes changing the name of the file you build by setting `base.archivesName` (this is typically set to your mod id).

```gradle
// In some build.gradle
base.archivesName = 'mymod'
```

#### Group Id

The `group` property should be set to your [top-level package][packaging], which should either be a domain you own or your email address:

Type      | Value             | Top-Level Package
:---:     | :---:             | :---
Domain    | example.com       | `com.example`
Subdomain | example.github.io | `io.github.example`
Email     | example@gmail.com | `com.gmail.example`

```gradle
// In some build.gradle
group = 'com.example'
```

The packages within your java source (`src/main/java`) should also now conform to this structure, with an inner package representing the mod id:

```text
com
- example (top-level package specified in group property)
  - mymod (the mod id)
    - MyMod.java (renamed ExampleMod.java)
```

#### Version

Set the `version` property to the current version of your mod. We recommend using a [variation of Maven versioning][mvnver].

```gradle
// In some build.gradle
version = '1.21.1-1.0.0.0'
```

### Additional Configurations

Additional configurations can be found on the [ForgeGradle] docs.

Building and Testing Your Mod
-----------------------------

1. To build your mod, run `gradlew build`. This will output a file in `build/libs` with the name `[archivesBaseName]-[version].jar`, by default. This file can be placed in the `mods` folder of a Forge-enabled Minecraft setup or distributed.
1. To run your mod in a test environment, you can either use the generated run configurations or use the associated tasks (e.g. `gradlew runClient`). This will launch Minecraft from the run directory (default 'run') along with any source sets specified. The default MDK includes the `main` source set, so any code written in `src/main/java` will be applied.
1. If you are running a dedicated server, whether through the run configuration or `gradlew runServer`, the server will initially shut down immediately. You will need to accept the Minecraft EULA by editing the `eula.txt` file in the run directory. Once accepted, the server will load, which can then be accessed via a direct connect to `localhost`.

!!! note
    You should always test your mod in a dedicated server environment. This includes [client-only mods][client] as they should not do anything when loaded on the server.

[jdk]: https://adoptium.net/temurin/releases?version=17 "Eclipse Temurin 17 Prebuilt Binaries"
[ForgeGradle]: https://docs.minecraftforge.net/en/fg-6.x

[files]: https://files.minecraftforge.net "Forge Files distribution site"
[config]: https://docs.minecraftforge.net/en/fg-6.x/configuration/runs/

[modfiles]: ./modfiles.md
[packaging]: ./structuring.md#packaging
[mvnver]: ./versioning.md
[client]: ../concepts/sides.md#writing-one-sided-mods

---

Mod Files
=========

The mod files are responsible for determining what mods are packaged into your JAR, what information to display within the 'Mods' menu, and how your mod should be loaded in the game.

mods.toml
---------

The `mods.toml` file defines the metadata of your mod(s). It also contains additional information that is displayed within the 'Mods' menu and how your mod(s) should be loaded into the game.

The file uses the [Tom's Obvious Minimal Language, or TOML][toml], format. The file must be stored under the `META-INF` folder in the resource directory of the source set you are using (`src/main/resources/META-INF/mods.toml` for the `main` source set). A `mods.toml` file may look something like this:

```toml
modLoader="javafml"
loaderVersion="[52,)"

license="All Rights Reserved"
issueTrackerURL="https://github.com/MinecraftForge/MinecraftForge/issues"
showAsResourcePack=false
clientSideOnly=false

[[mods]]
  modId="examplemod"
  version="1.0.0.0"
  displayName="Example Mod"
  updateJSONURL="https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
  displayURL="https://minecraftforge.net"
  logoFile="logo.png"
  credits="I'd like to thank my mother and father."
  authors="Author"
  description='''
  Lets you craft dirt into diamonds. This is a traditional mod that has existed for eons. It is ancient. The holy Notch created it. Jeb rainbowfied it. Dinnerbone made it upside down. Etc.
  '''
  displayTest="MATCH_VERSION"

[[dependencies.examplemod]]
  modId="forge"
  mandatory=true
  versionRange="[52,)"
  ordering="NONE"
  side="BOTH"

[[dependencies.examplemod]]
  modId="minecraft"
  mandatory=true
  versionRange="[1.21.1,)"
  ordering="NONE"
  side="BOTH"
```

`mods.toml` is broken into three parts: the non-mod-specific properties, which are linked to the mod file; the mod properties, with a section for each mod; and the dependency configurations, with a section for each mod's or mods' dependencies. Each of the properties associated with the `mods.toml` file will be explained below, where `required` means that a value must be specified or an exception will be thrown.

### Non-Mod-Specific Properties

Non-mod-specific properties are properties associated with the JAR itself, indicating how to load the mod(s) and any additional global metadata.

Property             | Type    | Default       | Description | Example
:---                 | :---:   | :---:         | :---:       | :---
`modLoader`          | string  | **mandatory** | The language loader used by the mod(s). Can be used to support alternative language structures, such as Kotlin objects for the main file, or different methods of determining the entrypoint, such as an interface or method. Forge provides the Java loader `"javafml"` and low/no code loader `"lowcodefml"`. | `"javafml"`
`loaderVersion`      | string  | **mandatory** | The acceptable version range of the language loader, expressed as a [Maven Version Range][mvr]. For `javafml` and `lowcodefml`, the version is the major version of the Forge version. | `"[46,)"`
`license`            | string  | **mandatory** | The license the mod(s) in this JAR are provided under. It is suggested that this is set to the [SPDX identifier][spdx] you are using and/or a link to the license. You can visit https://choosealicense.com/ to help pick the license you want to use. | `"MIT"`
`showAsResourcePack` | boolean | `false`       | When `true`, the mod(s)'s resources will be displayed as a separate resource pack on the 'Resource Packs' menu, rather than being combined with the 'Mod resources' pack. | `true`
`clientSideOnly`     | boolean | `false`       | When `true`, Forge will skip loading all mods declared in the mods.toml when running on a dedicated server, and set a correct `displayTest` for each of them when running on a client. | `true`
`services`           | array   | `[]`          | An array of services your mod **uses**. This is consumed as part of the created module for the mod from Forge's implementation of the Java Platform Module System. This is deprecated in favour of the standard Java methods for declaring services, namely individual service files or module-info.java [`uses` directive][uses] | `["net.minecraftforge.forgespi.language.IModLanguageProvider"]`
`properties`         | table   | `{}`          | A table of substitution properties. This is used by `StringSubstitutor` to replace `${file.<key>}` with its corresponding value. This is currently only used to replace the `version` in the [mod-specific properties][modsp]. | `{ "example" = "1.2.3" }` referenced by `${file.example}`
`issueTrackerURL`    | string  | *nothing*     | A URL representing the place to report and track issues with the mod(s). | `"https://forums.minecraftforge.net/"`

!!! important
    The `services` property is functionally equivalent to specifying the [`uses` directive in a module][uses], which allows [*loading*][serviceload] a service of a given type.

### Mod-Specific Properties

Mod-specific properties are tied to the specified mod using the `[[mods]]` header. This is an [array of tables][array]; all key/value properties will be attached to that mod until the next header.

```toml
# Properties for examplemod1
[[mods]]
modId = "examplemod1"

# Properties for examplemod2
[[mods]]
modId = "examplemod2"
```

Property        | Type    | Default                 | Description | Example
:---            | :---:   | :---:                   | :---:       | :---
`modId`         | string  | **mandatory**           | The unique identifier representing this mod. The id must match `^[a-z][a-z0-9_]{1,63}$` (a string 2-64 characters; starts with a lowercase letter; made up of lowercase letters, numbers, or underscores). | `"examplemod"`
`namespace`     | string  | value of `modId`        | An override namespace for the mod. The namespace much match `^[a-z][a-z0-9_.-]{1,63}$` (a string 2-64 characters; starts with a lowercase letter; made up of lowercase letters, numbers, underscores, dots, or dashes). Currently unused. | `"example"`
`version`       | string  | `"1"`                   | The version of the mod, preferably in a [variation of Maven versioning][mvnver]. When set to `${file.jarVersion}`, it will be replaced with the value of the `Implementation-Version` property in the JAR's manifest (displays as `0.0NONE` in a development environment). | `"1.21.1-1.0.0.0"`
`displayName`   | string  | value of `modId`        | The pretty name of the mod. Used when representing the mod on a screen (e.g., mod list, mod mismatch). | `"Example Mod"`
`description`   | string  | `"MISSING DESCRIPTION"` | The description of the mod shown in the mod list screen. It is recommended to use a [multiline literal string][multiline]. | `"This is an example."`
`logoFile`      | string  | *nothing*               | The name and extension of an image file used on the mods list screen. The logo must be in the root of the JAR or directly in the root of the source set (e.g., `src/main/resources` for the main source set). | `"example_logo.png"`
`logoBlur`      | boolean | `true`                  | Whether to use `GL_LINEAR*` (true) or `GL_NEAREST*` (false) to render the `logoFile`. | `false`
`updateJSONURL` | string  | *nothing*               | A URL to a JSON used by the [update checker][update] to make sure the mod you are playing is the latest version. | `"https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"`
`features`      | table   | `{}`                    | See '[features]'. | `{ java_version = "17" }`
`modproperties` | table   | `{}`                    | A table of key/values associated with this mod. Currently unused by Forge, but is mainly for use by mods. | `{ example = "value" }` 
`modUrl`        | string  | *nothing*               | A URL to the download page of the mod. Currently unused. | `"https://files.minecraftforge.net/"`
`credits`       | string  | *nothing*               | Credits and acknowledges for the mod shown on the mod list screen. | `"The person over here and there."`
`authors`       | string  | *nothing*               | The authors of the mod shown on the mod list screen. | `"Example Person"`
`displayURL`    | string  | *nothing*               | A URL to the display page of the mod shown on the mod list screen. | `"https://minecraftforge.net/"`
`displayTest`   | string  | `"MATCH_VERSION"`       | See '[sides]'. | `"NONE"`

#### Features

The features system allows mods to demand that certain settings, software, or hardware are available when loading the system. When a feature is not satisfied, mod loading will fail, informing the user about the requirement. Currently, Forge provides the following features:

Feature        | Description | Example
:---:          | :---:       | :---
`java_version` | The acceptable version range of the Java version, expressed as a [Maven Version Range][mvr]. This should be the supported version used by Minecraft. | `"[17,)"`

### Dependency Configurations

Mods can specify their dependencies, which are checked by Forge before loading the mods. These configurations are created using the [array of tables][array] `[[dependencies.<modid>]]` where `modid` is the identifier of the mod the dependency is for.

Property       | Type    | Default       | Description | Example
:---           | :---:   | :---:         | :---:       | :---
`modId`        | string  | **mandatory** | The identifier of the mod added as a dependency. | `"example_library"`
`mandatory`    | boolean | **mandatory** | Whether the game should crash when this dependency is not met. | `true`
`versionRange` | string  | `""`          | The acceptable version range of the language loader, expressed as a [Maven Version Range][mvr]. An empty string matches any version. | `"[1, 2)"`
`ordering`     | string  | `"NONE"`      | Defines if the mod must load before (`"BEFORE"`) or after (`"AFTER"`) this dependency. If the ordering does not matter, return `"NONE"` | `"AFTER"`
`side`         | string  | `"BOTH"`      | The [physical side][dist] the dependency must be present on: `"CLIENT"`, `"SERVER"`, or `"BOTH"`.| `"CLIENT"`
`referralUrl`  | string  | *nothing*     | A URL to the download page of the dependency. Currently unused. | `"https://library.example.com/"`

!!! warning
    The `ordering` of two mods may cause a crash due to a cyclic dependency: for example, mod A must load `"BEFORE"` mod B and mod B `"BEFORE"` mod A.

Mod Entrypoints
---------------

Now that the `mods.toml` is filled out, we need to provide an entrypoint to begin programming the mod. Entrypoints are essentially the starting point for executing the mod. The entrypoint itself is determined by the language loader used in the `mods.toml`.

### `javafml` and `@Mod`

`javafml` is a language loader provided by Forge for the Java programming language. The entrypoint is defined using a public class with the `@Mod` annotation. The value of `@Mod` must contain one of the mod ids specified within the `mods.toml`. From there, all initialization logic (e.g., [registering events][events], [adding `DeferredRegister`s][registration]) can be specified within the constructor of the class. The mod bus can be obtained from `FMLJavaModLoadingContext` which is fed through as a constructor parameter.

```java
@Mod("examplemod") // Must match mods.toml
public class Example {

  public Example(FMLJavaModLoadingContext context) {
    // Initialize logic here
    var modBus = context.getModEventBus();

    // ...
  }
}
```

### `lowcodefml`

`lowcodefml` is a language loader used as a way to distribute datapacks and resource packs as mods without the need of an in-code entrypoint. It is specified as `lowcodefml` rather than `nocodefml` for minor additions in the future that might require minimal coding.

[toml]: https://toml.io/
[mvr]: https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html
[spdx]: https://spdx.org/licenses/
[modsp]: #mod-specific-properties
[uses]: https://docs.oracle.com/javase/specs/jls/se17/html/jls-7.html#jls-7.7.3
[serviceload]: https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ServiceLoader.html#load(java.lang.Class)
[array]: https://toml.io/en/v1.0.0#array-of-tables
[mvnver]: ./versioning.md
[multiline]: https://toml.io/en/v1.0.0#string
[update]: ../misc/updatechecker.md
[features]: #features
[sides]: ../concepts/sides.md#writing-one-sided-mods
[dist]: ../concepts/sides.md#different-kinds-of-sides
[events]: ../concepts/events.md
[registration]: ../concepts/registries.md#deferredregister

---

Structuring Your Mod
====================

Structured mods are beneficial for maintenance, making contributions, and providing a clearer understanding of the underlying codebase. Some of the recommendations from Java, Minecraft, and Forge are listed below.

!!! note
    You do not have to follow the advice below; you can structure your mod any way you see fit. However, it is still highly recommended to do so.

Packaging
---------

When structuring your mod, pick a unique, top-level package structure. Many programmers will use the same name for different classes, interfaces, etc. Java allows classes to have the same name as long as they are in different packages. As such, if two classes have the same package with the same name, only one would be loaded, most likely causing the game to crash.

```
a.jar
  - com.example.ExampleClass
b.jar
  - com.example.ExampleClass // This class will not normally be loaded
```

This is even more relevant when it comes to loading modules. If there are class files in two packages under the same name in separate modules, this will cause the mod loader **to crash on startup** since mod modules are exported to the game and other mods.

```
module A
  - package X
    - class I
    - class J
module B
  - package X // This package will cause the mod loader to crash, as there already is a module with package X being exported
    - class R
    - class S
    - class T
```

As such, your top level package should be something that you own: a domain, email address, a subdomain of where your website, etc. It can even be your name or username as long as you can guarantee that it will be uniquely identifiable within the expected target.

Type      | Value             | Top-Level Package
:---:     | :---:             | :---
Domain    | example.com       | `com.example`
Subdomain | example.github.io | `io.github.example`
Email     | example@gmail.com | `com.gmail.example`

The next level package should then be your mod's id (e.g. `com.example.examplemod` where `examplemod` is the mod id). This will guarantee that, unless you have two mods with the same id (which should never be the case), your packages should not have any issues loading.

You can find some additional naming conventions on [Oracle's tutorial page][naming].

### Sub-package Organization

In addition to the top-level package, it is highly recommend to break your mod's classes between subpackages. There are two major methods on how to do so:

* **Group By Function**: Make subpackages for classes with a common purpose. For example, blocks can be under `block` or `blocks`, entities under `entity` or `entities`, etc. Mojang uses this structure with the singular version of the word.
* **Group By Logic**: Make subpackages for classes with a common logic. For example, if you were creating a new type of crafting table, you would put its block, menu, item, and more under `feature.crafting_table`.

#### Client, Server, and Data Packages

In general, code only for a given side or runtime should be isolated from the other classes in a separate subpackage. For example, code related to [data generation][datagen] should go in a `data` package while code only on the dedicated server should go in a `server` package.

However, it is highly recommended that [client-only code][sides] should be isolated in a `client` subpackage. This is because dedicated servers have no access to any of the client-only packages in Minecraft. As such, having a dedicated package would provide a decent sanity check to verify you are not reaching across sides within your mod.

Class Naming Schemes
--------------------

A common class naming scheme makes it easier to decipher the purpose of the class or to easily locate specific classes.

Classes are commonly suffixed with its type, for example:

* An `Item` called `PowerRing` -> `PowerRingItem`.
* A `Block` called `NotDirt` -> `NotDirtBlock`.
* A menu for an `Oven` -> `OvenMenu`.

!!! note
    Mojang typically follows a similar structure for all classes except entities. Those are represented by just their names (e.g. `Pig`, `Zombie`, etc.).

Choose One Method from Many
---------------------------

There are many methods for performing a certain task: registering an object, listening for events, etc. It's generally recommended to be consistent by using a single method to accomplish a given task. While this does improve code formatting, it also avoid any weird interactions or redundancies that may occur (e.g. your event listener executing twice).

[naming]: https://docs.oracle.com/javase/tutorial/java/package/namingpkgs.html
[datagen]: ../datagen/index.md
[sides]: ../concepts/sides.md

---

Versioning
==========

In general projects, [semantic versioning][semver] is often used (which has the format `MAJOR.MINOR.PATCH`). However, in the case of modding it may be more beneficial to use the format `MCVERSION-MAJORMOD.MAJORAPI.MINOR.PATCH` to be able to differentiate between world-breaking and API-breaking changes of a mod.

!!! important
    Forge uses [Maven version ranges][cmpver] to compare version strings, which is not fully compatible with the Semantic Versioning 2.0.0 spec, such as the 'prerelease' tag.

Examples
--------

Here is a list of examples that can increment the various variables.

* `MCVERSION`
  * Always matches the Minecraft version the mod is for.
* `MAJORMOD`
  * Removing items, blocks, block entities, etc.
  * Changing or removing previously existing mechanics.
  * Updating to a new Minecraft version.
* `MAJORAPI`
  * Changing the order or variables of enums.
  * Changing return types of methods.
  * Removing public methods altogether.
* `MINOR`
  * Adding items, blocks, block entities, etc.
  * Adding new mechanics.
  * Deprecating public methods. (This is not a `MAJORAPI` increment since it doesn't break an API.)
* `PATCH`
  * Bugfixes.

When incrementing any variable, all lesser variables should reset to `0`. For instance, if `MINOR` would increment, `PATCH` would become `0`. If `MAJORMOD` would increment, all other variables would become `0`.

### Work In Progress

If you are in the initial development stage of your mod (before any official releases), the `MAJORMOD` and `MAJORAPI` should always be `0`. Only `MINOR` and `PATCH` should be updated every time you build your mod. Once you build an official release (most of the time with a stable API), you should increment `MAJORMOD` to version `1.0.0.0`. For any further development stages, refer to the [Prereleases][pre] and [Release candidates][rc] section of this document.

### Multiple Minecraft Versions

If the mod upgrades to a new version of Minecraft, and the old version will only receive bug fixes, the `PATCH` variable should be updated based on the version before the upgrade. If the mod is still in active development in both the old and the new version of Minecraft, it is advised to append the version to **both** build numbers. For example, if the mod is upgraded to version `3.0.0.0` due to a Minecraft version change, the old mod should also be updated to `3.0.0.0`. The old version will become, for example, version `1.7.10-3.0.0.0`, while the new version will become `1.8-3.0.0.0`. If there are no changes at all when building for a newer Minecraft version, all variables except for the Minecraft version should stay the same.

### Final Release

When dropping support for a Minecraft version, the last build for that version should get the `-final` suffix. This denotes that the mod will no longer be supported for the denoted `MCVERSION` and that players should upgrade to a newer version of the mod to continue receiving updates and bug fixes.

### Pre-releases

It is also possible to prerelease work-in-progress features, which means new features are released that are not quite done yet. These can be seen as a sort of "beta". These versions should be appended with `-betaX`, where `X` is the number of the prerelease. (This guide does not use `-pre` since, at the time of writing, it is not a valid alias for `-beta`.) Note that already released versions and versions before the initial release can not go into prerelease; variables (mostly `MINOR`, but `MAJORAPI` and `MAJORMOD` can also prerelease) should be updated accordingly before adding the `-beta` suffix. Versions before the initial release are simply work-in-progress builds.

### Release Candidates

Release candidates act as prereleases before an actual version change. These versions should be appended with `-rcX`, where `X` is the number of the release candidate which should, in theory, only be increased for bugfixes. Already released versions can not receive release candidates; variables (mostly `MINOR`, but `MAJORAPI` and `MAJORMOD` can also prerelease)  should be updated accordingly before adding the `-rc` suffix. When releasing a release candidate as stable build, it can either be exactly the same as the last release candidate or have a few more bug fixes.

[semver]: https://semver.org/
[cmpver]: https://maven.apache.org/ref/3.5.2/maven-artifact/apidocs/org/apache/maven/artifact/versioning/ComparableVersion.html
[pre]: #pre-releases
[rc]: #release-candidates
