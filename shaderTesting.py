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
		    sys.exit("shader compilation failed")

if __name__ == "__main__":
    CompileShader("shaders/testShader")
    ri = prman.Ri()     # Create RenderMan interface instance

    ri.Begin("__render")    # Begin .rib and pass to renderer
    ri.Display("toiletroll.exr", "framebuffer", "rgba")       # File, Buffer, Colour Channels
    ri.Format(512, 512, 1)                              # Width, Height, Aspect Ratio

    # Camera coordinate system
    ri.Projection(ri.PERSPECTIVE)
    ri.Translate(0, 0, 2)

    # World coordinate system
    ri.WorldBegin()

    # Create surface
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Surface"})

    ri.Attribute('displacementbound', 
    {
        'sphere' : [1],
        'coordinatesystem' : ['object']
    })

    ri.Pattern('testShader','testShader',
    {
        
    })

    ri.Bxdf("PxrSurface", "roll",
    {
        "reference color diffuseColor" : ["testShader:resultRGB"],
    })

    cube_width = 5
    cube_height = 5
    cube_depth = 0.5
    CreateCube(cube_width, cube_height, cube_depth)
    ri.AttributeEnd()
    ri.TransformEnd()

    ri.WorldEnd()

    ri.End()    # End .rib