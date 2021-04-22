import prman
import sys
import sys, os.path, subprocess
import random

def CreateCube(_width = 1.0, _height = 1.0, _depth = 1.0):   
    # The following function is adapted from:
    # Macey, J,. 2020. Introduction to Renderman and Python. [online]
    # Available from: https://nccastaff.bournemouth.ac.uk/jmacey/msc/renderman/lectures/Lecture1/
    # Accessed [23 March 2021]
    w = _width / 2.0
    h = _height / 2.0
    d = _depth / 2.0

    # Apply texture
    ri.Pattern('table','table', 
    {
        # Texture acquired from:
        # Texture Haven,. 2021. plywood [online]
        # Available from: https://texturehaven.com/tex/?c=wood&t=plywood
        # Accessed [15 April 2021]
    	'string path' : ["images/textures/woodtest.tx"]
    })
    ri.Bxdf('PxrSurface', 'wood',
    {
    	'reference color diffuseColor' : ['table:resultRGB'],
    	'int diffuseDoubleSided' : [1],
    	'float reflectionGain' : [0.2]
	})

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

def CreateRoll(_height = 1.0, _outerRadius = 1.0, _innerRadius = 0.5, _pattern = "tissuePatternWave"):
    # Inner tube
    ri.AttributeBegin()
    Diffuse(0.45, 0.4, 0.33)
    ri.Cylinder(_innerRadius, -_height, _height, 360)
    ri.AttributeEnd()
    
    # Outer tube
    ri.AttributeBegin()
    ri.Attribute("displacementbound", 
    {
        "sphere" : [1],
        "coordinatesystem" : ["shader"]
    })
    noiseHeight = random.uniform(0.003, 0.007)
    noiseFreq = random.randint(5, 8)
    ri.Pattern(_pattern, _pattern,
    {
        "point circlesPerRing" : [50, 44, 36],
        "float height" : [noiseHeight],
        "int frequency" : [noiseFreq]

    })
    displacement = _pattern + ":dispOut"
    ri.Displace("PxrDisplace", "disp",
    {
        "reference float dispScalar" : [displacement]
    })
    colour = _pattern + ":resultRGB"
    ri.Bxdf("PxrSurface", "pattern",
    {
        "reference color diffuseColor" : [colour],
        'int diffuseDoubleSided' : [1],
        'float subsurfaceGain' : [0.3],
        'color subsurfaceColor' : [0.001,0.001,0.001],
        'float diffuseRoughness' : [0.7]
    })
    ri.Cylinder(_outerRadius, -_height, _height, 360)
    ri.AttributeEnd()

    # Top / Bottom
    ri.AttributeBegin()
    ri.Attribute('displacementbound', 
    {
        'sphere' : [1],
        'coordinatesystem' : ['shader']
    })
    noiseHeight = random.uniform(0.003, 0.005)
    noiseFreq = random.randint(195, 205)
    ri.Pattern('tissueNoise', 'tissueNoise',
    {
        #"float height" : [noiseHeight],
        "int frequency" : [noiseFreq]
    })
    ri.Displace('PxrDisplace', 'myDisp',
    {
        'reference float dispScalar' : ['tissueNoise:dispOut']
    })
    ri.Bxdf('PxrSurface', 'top',
    {
        'reference color diffuseColor' : ['tissueNoise:resultRGB'],
        'int diffuseDoubleSided' : [1],
        'float subsurfaceGain' : [0.3],
        'color subsurfaceColor' : [0.001,0.001,0.001],
        'float diffuseRoughness' : [0.7]
    })
    ri.Hyperboloid([_innerRadius, 0.0, -_height], [_outerRadius, 0.0, -_height], 360)
    ri.Hyperboloid([_innerRadius, 0.0, _height], [_outerRadius, 0.0, _height], 360)
    ri.AttributeEnd()

def CreateRollPyramid(_layers, _height = 1.0, _outerRadius = 1.0, _innerRadius = 0.5, _pattern = "tissuePatternWave"):
    pattern = _pattern
    for i in range(_layers):
        offset = (_layers - i) / 2.0
        currentRolls = _layers - i
        # Move to furthest left roll position
        ri.Translate(-(offset * _outerRadius * 2) + _outerRadius, 0, 0)

        for j in range(currentRolls):
            # Calculate random pattern and rotation
            angle = random.randint(0, 360)
            if pattern == "random":
                if random.randint(0, 1):
                    _pattern = "tissuePatternWave"
                else:
                    _pattern = "tissuePatternCircles"
                    
            # Create toilet roll
            ri.Rotate(angle, 0, 0, 1)
            CreateRoll(_height, _outerRadius, _innerRadius, _pattern)
            ri.Rotate(-angle, 0, 0, 1)
            
            # Move right
            if j < currentRolls - 1:
                ri.Translate(_outerRadius * 2, 0, 0)

        # Move to centre of next layer
        ri.Translate(-(offset * _outerRadius * 2) + _outerRadius, 0, -_height * 2)

def Diffuse(_r = 1.0, _g = 1.0, _b = 1.0):
    ri.Bxdf("PxrDiffuse", "diffuse", 
    {
        "color diffuseColor" : [_r, _g, _b]
    })

def CompileShader(_shader):
    # The following function is from:
    # Macey, J., 2018. Lecture4Shaders. [online]
    # Available from: https://github.com/NCCA/Renderman/blob/master/Lecture4Shaders/Bands/bands.py
    # Accessed [25 March 2021]
  	if os.path.isfile(_shader + ".oso") != True or os.stat(_shader + ".osl").st_mtime - os.stat(_shader + ".oso").st_mtime > 0:
	    print("compiling shader %s" %(_shader))
	    try:
		    subprocess.check_call(["oslc", _shader + ".osl"])
	    except subprocess.CalledProcessError:
		    sys.exit('shader compilation failed')

if __name__ == "__main__":
    CompileShader("shaders/tissuePatternCircles")
    CompileShader("shaders/tissuePatternWave")
    CompileShader("shaders/tissueNoise")
    CompileShader("shaders/table")

    ri = prman.Ri()     # Create RenderMan interface instance

    ri.Begin("__render")    # Begin .rib and pass to renderer
    ri.Display("toiletroll.exr", "framebuffer", "rgba")       # File, Buffer, Colour Channels
    ri.Format(1024, 1024, 1)                              # Width, Height, Aspect Ratio

    # Camera coordinate system
    ri.Projection(ri.PERSPECTIVE)
    ri.Translate(0, -2, 5)
    ri.Rotate(70, 1, 0, 0)

    # World coordinate system
    ri.WorldBegin()

    # Create roll
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Toilet Roll"})
    roll_height = 1.06
    roll_outerRadius = 1.04
    roll_innerRadius = 0.49
    #CreateRoll(roll_height, roll_outerRadius, roll_innerRadius, "tissuePatternCircles")
    CreateRollPyramid(3, 1.06, 1.04, 0.49, "random")
    ri.AttributeEnd()
    ri.TransformEnd()

    # Create table
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Table"})
    table_width = 6
    table_height = 4
    table_depth = 0.5
    ri.Translate(0, 0, roll_height + (table_depth / 2))
    CreateCube(table_width, table_height, table_depth)
    ri.AttributeEnd()
    ri.TransformEnd()

    # Create environment map
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Environment Map"})
    ri.Rotate(180, 1, 0, 0)
    ri.Rotate(-66, 0, 0, 1)
    ri.Light("PxrDomeLight", "EnvMapLight",
    {
        "float exposure" : [0],
        # HDRI acquired from:
        # HDRI Haven,. 2021. Lebombo [online]
        # Available from: https://hdrihaven.com/hdri/?c=indoor&h=lebombo
        # Accessed [21 April 2021]
        "string lightColorMap" : ["images/env-map/lebombo_4k.tx"]
    })
    ri.AttributeEnd()
    ri.TransformEnd()

    ri.WorldEnd()

    ri.End()    # End .rib