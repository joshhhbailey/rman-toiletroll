import prman

ri = prman.Ri()     # Create RenderMan interface instance

ri.Begin("__render")                                # Begin .rib and pass to renderer

ri.Display("Test.exr", "framebuffer", "rgba")       # File, Buffer, Colour Channels
ri.Format(512, 512, 1)                              # Width, Height, Aspect Ratio
ri.Projection(ri.PERSPECTIVE)                       # Camera coordinate system

ri.WorldBegin()             # World coordinate system
ri.Translate(0, 0, 5)
ri.TransformBegin()
ri.Rotate(60, 1, 0, 0)
ri.Cylinder(0.49, -1.06, 1.06, 360) # Inner tube
ri.Cylinder(1.04, -1.06, 1.06, 360) # Outer tube
ri.Hyperboloid([0.49, 0.0, -1.06],[1.04, 0.0, -1.06], 360)    # Top
ri.TransformEnd()

ri.WorldEnd()

ri.End()