# Versions in SAS Viya ARK

## Rationale for numbering

* Over time, SAS Viya ARK will evolve
    * possibly, some bugs need to be corrected
    * maybe some new features are added
    * a new version of SAS Viya is available, and SAS Viya ARK needs to be updated
* For all these reasons, SAS Viya ARK needs its own numbering scheme, distinct, and yet related to the Versions of SAS Viya itself
* Whenever you use SAS Viya ARK, make sure that you know which version you are using
* If you are unsure, check what the version at the top of the [ChangeLog](CHANGELOG.md) is
* If you contact SAS or Open an [issue](https://github.com/sassoftware/viya-ark/issues), make sure to mention the exact version of SAS Viya-ARK you are using. 

## Numbering scheme

* Example version
    * the first "modern" version of SAS Viya ARK was called **Viya34-ark-1.0**
    * `<viya_version>-ark-<first-digit>-<second-digit>`
    * let's decompose that into its consituing parts:

        | Viya34                | -  | ark     | -  | 1                 | . | 0                    | 
        |-----------------------|----|---------|----|-------------------|---|----------------------|
        | SAS Viya Version      |dash|         |dash| Major Version     |dot| Minor Version        |

* SAS Viya Version is an indicator of the **highest** version of SAS Viya that this has been tested with. 
    * Using Viya34-ark-X.X with a SAS Viya 3.5 deployment would likely **not** work.
    * Using Viya35.ark-X.X with a SAS Viya 3.4 Deployment would likely **not** work.
* SAS Viya ARK will not be backwards-compatible across SAS Viya releases.
    * In other words, you should aim to use the latest realease of SAS Viya ARK, as long as the ViyaXX portion matches the target software
    * It will be impossible to have a version of SAS Viya-ARK that is backwards compatible with much older versions of SAS Viya, and attempting it would prevent a healthy development of SAS Viya-ARK
* `ark` is used as a starting marker to show that this is the actual version number of SAS Viya-ARK, not of SAS Viya
* The Major Version number will be incremented when:
    * There are some major changes in SAS Viya itself, such as an Upgrade within a SAS Viya Version (e.g. SAS Viya 3.4 "May 2019 Upgrade" )
    * There are major changes in SAS Viya ARK itself, such as an important new feature
* The Minor Version number will be incremented when:
    * a bug is fixed 
    * some code is replaced with equivalent code that does not really change the behavior
    * small improvements are made, such as adding tags, spacing, etc..
* When the next release of SAS Viya is available, the digits are "reset": 
    * we might go from **Viya34-ark-5.2** to **Viya35-ark-1.0**
* Changes to the documentation (in the markdown files) will not necessarily trigger an increment in the version, as the documentation does not impact the way the softare runs. 

 


