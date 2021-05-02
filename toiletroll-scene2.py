import prman
import sys
import sys, os.path, subprocess
import random

# The following function is adapted from:
# Macey, J,. 2020. Introduction to Renderman and Python. [online]
# Available from: https://nccastaff.bournemouth.ac.uk/jmacey/msc/renderman/lectures/Lecture1/
# Accessed [23 March 2021]
def CreateCube(_width = 1.0, _height = 1.0, _depth = 1.0):   
    w = _width / 2.0
    h = _height / 2.0
    d = _depth / 2.0

    # Apply texture
    ri.Pattern("table","table",                                     # Texture acquired from:      
    {                                                               # Texture Haven,. 2021. plywood [online]
    	"string path" : ["images/textures/plywood_diff_1k.tx"]      # Available from: https://texturehaven.com/tex/?c=wood&t=plywood
    })                                                              # Accessed [15 April 2021]
    ri.Bxdf("PxrSurface", "wood",
    {
    	"reference color diffuseColor" : ["table:resultRGB"],
    	"int diffuseDoubleSided" : [1],
    	"float reflectionGain" : [0.2]
	})

    # Rear
    face = [-w, -h, d, -w, h, d, w, -h, d, w, h, d]                                
    ri.Patch("bilinear", {"P":face})
    # Front
    face = [-w, -h, -d, -w, h, -d, w, -h, -d, w, h, -d]                                
    ri.Patch("bilinear", {"P":face})
    # Left
    face = [-w, -h, -d, -w, h, -d, -w, -h, d, -w, h, d]                                    
    ri.Patch("bilinear", {"P":face})
    # Right
    face = [w, -h, -d, w, h, -d, w, -h, d, w, h, d]                                
    ri.Patch("bilinear", {"P":face})
    # Bottom
    face = [w, -h, d, w, -h, -d, -w, -h, d, -w, -h, -d]                                
    ri.Patch("bilinear", {"P":face})
    # Top
    face = [w, h, d, w, h, -d, -w, h, d, -w, h, -d]                                
    ri.Patch("bilinear", {"P":face})

def CreateRoll(_height = 1.0, _outerRadius = 1.0, _innerRadius = 0.5, _pattern = "tissuePatternWave", _new = True):
    # Inner tube
    ri.AttributeBegin()
    ri.Attribute("displacementbound", 
    {
        "sphere" : [0.1],
        "coordinatesystem" : ["object"]
    })
    noiseHeight = random.uniform(0.7, 0.8)
    noiseFreq = random.randint(70, 80)
    ri.Pattern("tube", "tube",
    {
        "float height" : [noiseHeight],
        "int frequency" : [noiseFreq]
        
    })
    ri.Displace("PxrDisplace", "disp",
    {
        "reference float dispScalar" : ["tube:dispOut"]
    })
    ri.Bxdf("PxrSurface", "pattern",
    {
        "reference color diffuseColor" : ["tube:resultRGB"],
        "int diffuseDoubleSided" : [1],
        "float diffuseRoughness" : [1.0],
        "float fuzzConeAngle" : [8.0],
        "float fuzzGain" : [1.0]
    })
    ri.Cylinder(_innerRadius, -_height, _height, 360)
    ri.AttributeEnd()
    
    # Outer tube
    if _new:
        ri.AttributeBegin()
        ri.Attribute("displacementbound", 
        {
            "sphere" : [0.1],
            "coordinatesystem" : ["object"]
        })
        noiseHeight = random.uniform(0.003, 0.007)
        noiseFreq = random.randint(5, 8)
        ri.Pattern(_pattern, _pattern,
        {
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
            "int diffuseDoubleSided" : [1],
            "float diffuseRoughness" : [1.0],
            "float fuzzConeAngle" : [8.0],
            "float fuzzGain" : [1.0]
        })
        ri.Cylinder(_outerRadius, -_height, _height, 360)
        ri.AttributeEnd()

        # Top / Bottom
        ri.AttributeBegin()
        ri.Attribute("displacementbound", 
        {
            "sphere" : [0.1],
            "coordinatesystem" : ["object"]
        })
        noiseHeight = random.uniform(0.003, 0.005)
        noiseFreq = random.randint(195, 205)
        ri.Pattern("tissueNoise", "tissueNoise",
        {
            "float height" : [noiseHeight],
            "int frequency" : [noiseFreq]
        })
        ri.Displace("PxrDisplace", "myDisp",
        {
            "reference float dispScalar" : ["tissueNoise:dispOut"]
        })
        ri.Bxdf("PxrSurface", "top",
        {
            "reference color diffuseColor" : ["tissueNoise:resultRGB"],
            "int diffuseDoubleSided" : [1],
            "float diffuseRoughness" : [1.0],
            "float fuzzConeAngle" : [8.0],
            "float fuzzGain" : [1.0]
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

# The following function is from:
# Macey, J., 2018. Lecture4Shaders. [online]
# Available from: https://github.com/NCCA/Renderman/blob/master/Lecture4Shaders/Bands/bands.py
# Accessed [25 March 2021]
def CompileShader(_shader):
  	if os.path.isfile(_shader + ".oso") != True or os.stat(_shader + ".osl").st_mtime - os.stat(_shader + ".oso").st_mtime > 0:
	    print("compiling shader %s" %(_shader))
	    try:
		    subprocess.check_call(["oslc", _shader + ".osl"])
	    except subprocess.CalledProcessError:
		    sys.exit("shader compilation failed")

# The following function is adapted from:
# RenderMan., 2021. RenderMan Documentation 20: Denoising. [online]
# Available from: https://renderman.pixar.com/resources/RenderMan_20/risDenoise.html
# Accessed [27 April 2021]
def SetupDisplay():
    # Beauty...
    ri.DisplayChannel("color Ci")
    ri.DisplayChannel("float a")
    ri.DisplayChannel("color mse",
        {"string source" : "color Ci", "string statistics" : "mse"})

    # Shading...
    ri.DisplayChannel("color albedo",
        {"string source" : "color lpe:nothruput;noinfinitecheck;noclamp;unoccluded;overwrite;C<.S'passthru'>*((U2L)|O)"})
    ri.DisplayChannel("color albedo_var",
        {"string source" : "color lpe:nothruput;noinfinitecheck;noclamp;unoccluded;overwrite;C<.S'passthru'>*((U2L)|O)", "string statistics" : "variance" } )
    ri.DisplayChannel("color diffuse",
        {"string source" : "color lpe:C(D[DS]*[LO])|O" })
    ri.DisplayChannel("color diffuse_mse",
        {"string source" : "color lpe:C(D[DS]*[LO])|O", "string statistics" : "mse"})
    ri.DisplayChannel("color specular",
        {"string source" : "color lpe:CS[DS]*[LO]"})
    ri.DisplayChannel("color specular_mse",
        {"string source" : "color lpe:CS[DS]*[LO]", "string statistics" : "mse"})

    # Geometry...
    ri.DisplayChannel("float z",
        {"string source" : "float z", "string filter" : "gaussian"})
    ri.DisplayChannel("float z_var",
        {"string source" : "float z", "string filter" : "gaussian", "string statistics" : "variance"})
    ri.DisplayChannel("normal normal",
        {"string source" : "normal Nn"})
    ri.DisplayChannel("normal normal_var",
        {"string source" : "normal Nn", "string statistics" : "variance"})
    ri.DisplayChannel("vector forward",
        {"string source"  : "vector motionFore"})
    ri.DisplayChannel("vector backward",
        {"string source" : "vector motionBack"})

    # Export to framebuffer or openexr
    ri.Display("toiletroll-02.exr", "openexr", "Ci,a,mse,albedo,albedo_var,diffuse,diffuse_mse,specular,specular_mse,z,z_var,normal,normal_var,forward,backward", {"int asrgba" : [1]})

    ri.Format(1920, 1080, 1)                              # Width, Height, Aspect Ratio
    ri.Hider("raytrace", {"int incremental" : [1]})
    ri.Integrator("PxrPathTracer", "integrator")

if __name__ == "__main__":
    CompileShader("shaders/tissuePatternCircles")
    CompileShader("shaders/tissuePatternWave")
    CompileShader("shaders/tissueNoise")
    CompileShader("shaders/tube")
    CompileShader("shaders/table")

    ri = prman.Ri()     # Create RenderMan interface instance
    ri.Begin("__render")    # Begin .rib and pass to renderer
    SetupDisplay()

    # Camera coordinate system
    ri.Projection(ri.PERSPECTIVE)
    ri.DepthOfField(3.0, 0.15, 2.5)

    ri.Translate(0, -1, 3.75)
    ri.Rotate(75, 1, 0, 0)

    # World coordinate system
    ri.WorldBegin()

    # Create roll
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute ("identifier", {"name": "Toilet Roll"})
    roll_height = 1.06
    roll_outerRadius = 1.04
    roll_innerRadius = 0.49
    CreateRoll(roll_height, roll_outerRadius, roll_innerRadius, "tissuePatternCircles", True)
    ri.Translate(2, 0.5, 0)
    CreateRoll(roll_height, roll_outerRadius, roll_innerRadius, "tissuePatternCircles", False)
    ri.Translate(-4, -1, 0.53)
    ri.Rotate(90, 0, 1, 0)
    ri.Rotate(55, 1, 0, 0)
    CreateRoll(roll_height, roll_outerRadius, roll_innerRadius, "tissuePatternCircles", False)
    #CreateRollPyramid(2, roll_height, roll_outerRadius, roll_innerRadius, "random")
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
    ri.Light("PxrDomeLight", "EnvMapLight",                         # HDRI acquired from:
    {                                                               # HDRI Haven,. 2021. Lebombo [online]
        "float exposure" : [-0.25],                                 # Available from: https://hdrihaven.com/hdri/?c=indoor&h=lebombo
        "string lightColorMap" : ["images/env-map/lebombo_4k.tx"]   # Accessed [21 April 2021]
    })
    ri.AttributeEnd()
    ri.TransformEnd()

    ri.WorldEnd()

    ri.End()    # End .rib