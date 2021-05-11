##as_build_rig

This task calls Advanced skeleton to build the animation rig from a fit skeleton.

#### Requires
Advanced Skeleton


###Workflow:

#####1) Install Advanced Skeleton for Maya

#####2) Create a Maya project 
The name of the Maya project must match the asset's name

#####3) Create "fit" skeleton Maya file.
This is an advanced skeleton fit skeleton.  The model should be referenced
into this scene with "model" as the namespace.  Save as "<asset>_fit_v#.ma"

#####4) Create a "build" Maya file.  
This can be an empty scene or it can have whatever nodes you need.
This can reside in the scenes directory.  Save as "<asset>_build_v#.ma"

#####5) Create "blueprint" file.
This defines a sequence of build "tasks" that will be executed to construct the rig.

    Top Node
        - defines top node of rig
        
    Create Category
        - creates the sub groups under the top node of the rig
        
    Advanced Skeleton - Build Rig
        - builds the animation rig (and optional mocap rig) from a fit skeleton
        
    Advanced Skeleton - Modify Rig
        - makes custom modifications to the animation rig
        
    Import File References
        - imports any referenced files in the scene
        
    Remove Namespaces
        - removes all namespaces in scene
        
        
####TO DO
    - Add IK fingers
        
        
####PROPOSED NEW DIRECTORY STRUCTURE      
####<asset_name>\
    - data\ (json, yaml, xml, mel, python files)
    - export\ (fbx, obj)
    - scenes\ (working area)
    - assets\ (face rigs, imported rig files)
    - fit\ (versioned fit skeleton files)
    - model\ (versioned model files)
