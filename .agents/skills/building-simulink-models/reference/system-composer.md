# System Composer Architecture Model Rules

To create a new blank System Composer Architecture model, use `matlab_execute_code` with `systemcomposer.createModel("<ModelName>")`. Then modify with local Simulink edit tools or `matlab_execute_code` for System Composer APIs that are not exposed as dedicated tools.

## Key Differences from Standard Simulink

- **Components** are created with `type: "SubSystem"` -- they become architecture components automatically
- **Architecture ports** are created by adding In/Out Bus Element blocks inside a component -- the block name becomes the architecture port name
- Discover available port names with `simulink_get_param`, `simulink_find_blocks`, or targeted `matlab_execute_code` queries before connecting

## Creating a Component with Named Ports

1. Add component at root scope:
   `{"op": "add_block", "type": "SubSystem", "name": "Sensor", "ref": "s1"}`

2. Inside the component (scope = blk_ID of Sensor), add bus element ports:
   `{"op": "add_block", "type": "simulink/Ports & Subsystems/In Bus Element", "name": "Voltage"}`
   `{"op": "add_block", "type": "simulink/Ports & Subsystems/Out Bus Element", "name": "Torque"}`

3. Connect from root scope using the `blk_id` returned in the `created` map:
   `{"op": "connect", "target": "blk_<Source>.y1 -> blk_<Sensor>.Voltage"}`

## Creating Behavior Models from Architecture Components

Use `matlab_execute_code` with `systemcomposer.createSimulinkBehavior` to create a behavior model with matching interfaces:

```matlab
model = systemcomposer.loadModel('MyArchModel');
comp = lookup(model, Path="MyArchModel/Plant");
createSimulinkBehavior(comp, 'Plant_impl');
```

This creates `Plant_impl.slx` with ports matching the architecture component's interface. Repeat for each leaf component. Then use local Simulink edit tools on each generated behavior model to build the block diagrams inside.
