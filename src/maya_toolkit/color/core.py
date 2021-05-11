# built-ins
import os
import logging

# third party
import yaml
import maya.cmds as cmds


LOG = logging.getLogger(__name__)
level = logging.getLevelName('INFO')
LOG.setLevel(level)
DEFAULT_COLORS_DATA = os.path.join(os.path.dirname(__file__), 'default_colors.yml')


def get_color_data(colorValue, colorDataFile=DEFAULT_COLORS_DATA):

    color_file = open(colorDataFile, 'r')
    color_data = yaml.load(color_file)
    sides = color_data['SIDE_COLOR']

    if color_data.has_key(colorValue):
        var = color_data[colorValue]
    elif colorValue in sides:
        side_color = sides.get(colorValue)
        var = color_data[side_color]
    else:
        LOG.error("{} color not found in color data, please use:".format(colorValue))
        for k, v in color_data.iteritems():
            print k
        return False
    return var

def set_color(node, color):
    """Sets the maya color on a node like a control or transform

    args:
		node - type:string - the node you want to set the color of
		color - either a int(index), tuple(rgb) or string (preset color from yaml file)

    example:
        # Set by named preset
		set_color('Lf_arm_ik_ctrl', 'RED')
		set_color('Lf_arm_ik_ctrl', 'LEFT')
		set_color('Lf_arm_ik_ctrl', 'CENTER')

		# Set by rgb
		set_color('Lf_arm_ik_ctrl', (255, 0, 0))

		# Set by index
		set_color('Lf_arm_ik_ctrl', 13)

    """
    # Resolve if color is int, tuple or string

    # Index color
    if isinstance(color, int):
        colorIdx = color

        cmds.setAttr(node + '.overrideRGBColors', 0)
        cmds.setAttr(node + '.overrideEnabled', 1)
        cmds.setAttr(node + '.overrideShading', 0)
        cmds.setAttr(node + '.overrideColor', colorIdx)

        LOG.debug("Color = Index")

        return True

    # Rgb color
    elif isinstance(color, tuple):
        colorRgb = color
        LOG.debug("Color = RGB")

    # Preset color
    elif isinstance(color, str):
        if 'NONE' in color:
            cmds.setAttr(node + '.overrideRGBColors', 0)
            cmds.setAttr(node + '.overrideEnabled', 1)
            cmds.setAttr(node + '.overrideShading', 0)
            cmds.setAttr(node + '.overrideColor', 5)
            cmds.setAttr(node + '.overrideEnabled', 0)
            return True
        else:
            colorRgb = get_color_data(color)
            if colorRgb:
                color = colorRgb[1].split(',')
                LOG.debug("Color = PRESET")
            else:
                LOG.error("{} is not a supported color preset, see supported colors above".format(color))
                return False

    # Invalid input
    else:
        LOG.error("Input color {} is invalid".format(color))
        return False

    cmds.setAttr(node + '.overrideRGBColors', 1)
    cmds.setAttr(node + '.overrideEnabled', 1)
    cmds.setAttr(node + '.overrideShading', 0)
    cmds.setAttr(node + '.overrideColorRGB', int(color[0]), int(color[1]), int(color[2]) )

    return True


def control_color_to_shapes():
    """Moves override color from transform to shape"""
    sel = cmds.ls(selection=True)

    if sel:
        for ctl in sel:
            # Get color info
            rgb_colors = cmds.getAttr('{}.overrideRGBColors'.format(ctl))
            override_enabled = cmds.getAttr('{}.overrideEnabled'.format(ctl))
            override_shading = cmds.getAttr('{}.overrideShading'.format(ctl))
            override_color_rgb = cmds.getAttr('{}.overrideColorRGB'.format(ctl))[0]
            print override_color_rgb

            # Get curve shapes
            shps = cmds.listRelatives(ctl, shapes=True, type="nurbsCurve")

            # Copy color settings
            if shps:
                for shp in shps:
                    if not cmds.getAttr('{}.overrideEnabled'.format(shp)):
                        cmds.setAttr('{}.overrideRGBColors'.format(shp), rgb_colors)
                        cmds.setAttr('{}.overrideEnabled'.format(shp), override_enabled)
                        cmds.setAttr('{}.overrideShading'.format(shp), override_shading)
                        cmds.setAttr('{}.overrideColorRGB'.format(shp), override_color_rgb[0], override_color_rgb[1],
                                     override_color_rgb[2])

            # Reset color on original
            cmds.setAttr('{}.overrideEnabled'.format(ctl), 0)
