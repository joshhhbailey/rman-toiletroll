import prman
import sys
import sys,os.path,subprocess

def CreateCube(width = 1.0, height = 1.0, depth = 1.0):   
    # The following function is from:
    # Macey, J,. 2020. Introduction to Renderman and Python. [online]
    # Available from: https://nccastaff.bournemouth.ac.uk/jmacey/msc/renderman/lectures/Lecture1/
    # Accessed [23 March 2021]
    w = width / 2.0
    h = height / 2.0
    d = depth / 2.0
    # Rear
    face = [-w, -h, d, -w, h, d, w, -h, d, w, h, d]                                
    ri.Patch("bilinear", {'P':face})
    # Front
    face = [-w, -h, -d, -w, h, -d, w, -h, -d, w, h, -d]                                
    ri.Patch("bilinear", {'P':face})
    # Left
    face = [-w, -h, -d, -w, h, -d, -w, -h, d, -w, h, d]                                    
    ri.Patch("bilinear", {'P':face})
    # Right
    face = [w, -h, -d, w, h, -d, w, -h, d, w, h, d]                                
    ri.Patch("bilinear", {'P':face})
    # Bottom
    face = [w, -h, d, w, -h, -d, -w, -h, d, -w, -h, -d]                                
    ri.Patch("bilinear", {'P':face})
    # Top
    face = [w, h, d, w, h, -d, -w, h, d, -w, h, -d]                                
    ri.Patch("bilinear", {'P':face})

def CreateRoll(height = 1.0, outerRadius = 1.0, innerRadius = 0.5):
    # Inner tube
    ri.AttributeBegin()
    Diffuse(0.45, 0.4, 0.33)
    ri.Cylinder(innerRadius, -height, height, 360)
    ri.AttributeEnd()
    # Outer tube
    ri.AttributeBegin()
    ri.Attribute("displacementbound", 
    {
        "sphere" : [1],
        "coordinatesystem" : ["shader"]
    })
    # Apply shader
    ri.Pattern("rollPattern", "rollPattern",
    {
        "point circlesPerRing" : [50, 44, 36]
    })
    # Displace shader
    ri.Displace("PxrDisplace", "disp",
    {
        "reference float dispScalar" : ["rollPattern:dispOut"]
    })
    ri.Bxdf("PxrSurface", "surf",
    {
        "reference color diffuseColor" : ["rollPattern:resultRGB"],
    })
    ri.Cylinder(outerRadius, -height, height, 360)
    ri.AttributeEnd()
    # Top
    ri.Hyperboloid([innerRadius, 0.0, -height], [outerRadius, 0.0, -height], 360)

def Diffuse(r = 1.0, g = 1.0, b = 1.0):
    ri.Bxdf( 'PxrDiffuse','diffuse', 
    {
    'color diffuseColor' : [r, g, b]
    })

def CompileShader(shader):
    # The following function is from:
    # Macey, J., 2018. Lecture4Shaders. [online]
    # Available from: https://github.com/NCCA/Renderman/blob/master/Lecture4Shaders/Bands/bands.py
    # Accessed [25 March 2021]
  	if os.path.isfile(shader + ".oso") != True or os.stat(shader + ".osl").st_mtime - os.stat(shader + ".oso").st_mtime > 0:
	    print("compiling shader %s" %(shader))
	    try:
		    subprocess.check_call(["oslc", shader + ".osl"])
	    except subprocess.CalledProcessError:
		    sys.exit('shader compilation failed')

if __name__ == "__main__":
    CompileShader("rollPattern")
    ri = prman.Ri()     # Create RenderMan interface instance

    ri.Begin("__render")    # Begin .rib and pass to renderer
    ri.Display("toiletroll.exr", "framebuffer", "rgba")       # File, Buffer, Colour Channels
    ri.Format(1024, 1024, 1)                              # Width, Height, Aspect Ratio

    # Camera coordinate system
    ri.Projection(ri.PERSPECTIVE)
    ri.Translate(0, 0, 5)
    ri.Rotate(50, 1, 0, 0)

    # World coordinate system
    ri.WorldBegin()

    # Create roll
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Toilet Roll"})
    Diffuse(1.0, 1.0, 1.0)
    roll_height = 1.06
    roll_outerRadius = 1.04
    roll_innerRadius = 0.49
    CreateRoll(roll_height, roll_outerRadius, roll_innerRadius)
    ri.AttributeEnd()
    ri.TransformEnd()

    # Create surface
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Surface"})
    Diffuse(0.95, 0.8, 0.43)
    cube_width = 5
    cube_height = 5
    cube_depth = 0.5
    ri.Translate(0, 0, roll_height + (cube_depth / 2))
    CreateCube(cube_width, cube_height, cube_depth)
    ri.AttributeEnd()
    ri.TransformEnd()

    ri.WorldEnd()

    ri.End()    # End .rib