import six

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import image_comparison

from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1 import AxesGrid
from mpl_toolkits.axes_grid1.inset_locator import (
    zoomed_inset_axes,
    mark_inset,
    inset_axes,
    BboxConnectorPatch
)
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

from matplotlib.colors import LogNorm
from matplotlib.transforms import Bbox, TransformedBbox, \
     blended_transform_factory
from itertools import product

import numpy as np


@image_comparison(baseline_images=['divider_append_axes'])
def test_divider_append_axes():

    # the random data
    np.random.seed(0)
    x = np.random.randn(1000)
    y = np.random.randn(1000)

    fig, axScatter = plt.subplots()

    # the scatter plot:
    axScatter.scatter(x, y)

    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(axScatter)
    axHistbot = divider.append_axes("bottom", 1.2, pad=0.1, sharex=axScatter)
    axHistright = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)
    axHistleft = divider.append_axes("left", 1.2, pad=0.1, sharey=axScatter)
    axHisttop = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHisttop.hist(x, bins=bins)
    axHistbot.hist(x, bins=bins)
    axHistleft.hist(y, bins=bins, orientation='horizontal')
    axHistright.hist(y, bins=bins, orientation='horizontal')

    axHistbot.invert_yaxis()
    axHistleft.invert_xaxis()

    axHisttop.xaxis.set_ticklabels(())
    axHistbot.xaxis.set_ticklabels(())
    axHistleft.yaxis.set_ticklabels(())
    axHistright.yaxis.set_ticklabels(())


@image_comparison(baseline_images=['twin_axes_empty_and_removed'],
                  extensions=["png"], tol=1)
def test_twin_axes_empty_and_removed():
    # Purely cosmetic font changes (avoid overlap)
    matplotlib.rcParams.update({"font.size": 8})
    matplotlib.rcParams.update({"xtick.labelsize": 8})
    matplotlib.rcParams.update({"ytick.labelsize": 8})
    generators = [ "twinx", "twiny", "twin" ]
    modifiers = [ "", "host invisible", "twin removed", "twin invisible",
        "twin removed\nhost invisible" ]
    # Unmodified host subplot at the beginning for reference
    h = host_subplot(len(modifiers)+1, len(generators), 2)
    h.text(0.5, 0.5, "host_subplot", horizontalalignment="center",
        verticalalignment="center")
    # Host subplots with various modifications (twin*, visibility) applied
    for i, (mod, gen) in enumerate(product(modifiers, generators),
        len(generators)+1):
        h = host_subplot(len(modifiers)+1, len(generators), i)
        t = getattr(h, gen)()
        if "twin invisible" in mod:
            t.axis[:].set_visible(False)
        if "twin removed" in mod:
            t.remove()
        if "host invisible" in mod:
            h.axis[:].set_visible(False)
        h.text(0.5, 0.5, gen + ("\n" + mod if mod else ""),
            horizontalalignment="center", verticalalignment="center")
    plt.subplots_adjust(wspace=0.5, hspace=1)


def test_axesgrid_colorbar_log_smoketest():
    fig = plt.figure()
    grid = AxesGrid(fig, 111,  # modified to be only subplot
                    nrows_ncols=(1, 1),
                    label_mode="L",
                    cbar_location="top",
                    cbar_mode="single",
                    )

    Z = 10000 * np.random.rand(10, 10)
    im = grid[0].imshow(Z, interpolation="nearest", norm=LogNorm())

    grid.cbar_axes[0].colorbar(im)


@image_comparison(
    baseline_images=['inset_locator'], style='default', extensions=['png'],
    remove_text=True)
def test_inset_locator():
    def get_demo_image():
        from matplotlib.cbook import get_sample_data
        import numpy as np
        f = get_sample_data("axes_grid/bivariate_normal.npy", asfileobj=False)
        z = np.load(f)
        # z is a numpy array of 15x15
        return z, (-3, 4, -4, 3)

    fig, ax = plt.subplots(figsize=[5, 4])

    # prepare the demo image
    Z, extent = get_demo_image()
    Z2 = np.zeros([150, 150], dtype="d")
    ny, nx = Z.shape
    Z2[30:30 + ny, 30:30 + nx] = Z

    # extent = [-3, 4, -4, 3]
    ax.imshow(Z2, extent=extent, interpolation="nearest",
              origin="lower")

    axins = zoomed_inset_axes(ax, 6, loc=1)  # zoom = 6
    axins.imshow(Z2, extent=extent, interpolation="nearest",
                 origin="lower")
    axins.yaxis.get_major_locator().set_params(nbins=7)
    axins.xaxis.get_major_locator().set_params(nbins=7)
    # sub region of the original image
    x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    plt.xticks(visible=False)
    plt.yticks(visible=False)

    # draw a bbox of the region of the inset axes in the parent axes and
    # connecting lines between the bbox and the inset axes area
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    asb = AnchoredSizeBar(ax.transData,
                          0.5,
                          '0.5',
                          loc=8,
                          pad=0.1, borderpad=0.5, sep=5,
                          frameon=False)
    ax.add_artist(asb)


@image_comparison(
    baseline_images=['inset_axes'], style='default', extensions=['png'],
    remove_text=True)
def test_inset_axes():
    def get_demo_image():
        from matplotlib.cbook import get_sample_data
        import numpy as np
        f = get_sample_data("axes_grid/bivariate_normal.npy", asfileobj=False)
        z = np.load(f)
        # z is a numpy array of 15x15
        return z, (-3, 4, -4, 3)

    fig, ax = plt.subplots(figsize=[5, 4])

    # prepare the demo image
    Z, extent = get_demo_image()
    Z2 = np.zeros([150, 150], dtype="d")
    ny, nx = Z.shape
    Z2[30:30 + ny, 30:30 + nx] = Z

    # extent = [-3, 4, -4, 3]
    ax.imshow(Z2, extent=extent, interpolation="nearest",
              origin="lower")

    # creating our inset axes without a bbox_transform parameter
    axins = inset_axes(ax, width=1., height=1., bbox_to_anchor=(1, 1))

    axins.imshow(Z2, extent=extent, interpolation="nearest",
                 origin="lower")
    axins.yaxis.get_major_locator().set_params(nbins=7)
    axins.xaxis.get_major_locator().set_params(nbins=7)
    # sub region of the original image
    x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    plt.xticks(visible=False)
    plt.yticks(visible=False)

    # draw a bbox of the region of the inset axes in the parent axes and
    # connecting lines between the bbox and the inset axes area
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    asb = AnchoredSizeBar(ax.transData,
                          0.5,
                          '0.5',
                          loc=8,
                          pad=0.1, borderpad=0.5, sep=5,
                          frameon=False)
    ax.add_artist(asb)


def test_inset_axes_without_transform_should_use_parent_axes():
    # creating our figure
    fig = plt.figure(dpi=150)

    # gca method gets current axes of the figure
    ax = plt.gca()
    ax.plot([0.0, 0.25, 0.50, 1.0], [0.1, 0.2, 0.4, 0.9], color='b')

    # creating our inset_axes. without a bbox_transform parameter
    ax_ins = inset_axes(ax, width=1., height=1., bbox_to_anchor=(1, 1))
    ax_ins.plot([0.0, 0.25, 0.50, 1.0], [0.9, 0.4, 0.2, 0.1], color='r')

    assert ax.transAxes == ax_ins.transAxes


@image_comparison(
    baseline_images=['fill_facecolor'], extensions=['png'],
    remove_text=True, style='mpl20')
def test_fill_facecolor():
    fig, ax = plt.subplots(1, 5)
    fig.set_size_inches(5, 5)
    for i in range(1, 4):
        ax[i].yaxis.set_visible(False)
    ax[4].yaxis.tick_right()
    bbox = Bbox.from_extents(0, 0.4, 1, 0.6)

    # fill with blue by setting 'fc' field
    bbox1 = TransformedBbox(bbox, ax[0].transData)
    bbox2 = TransformedBbox(bbox, ax[1].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox1, bbox2, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", fc="b")
    p.set_clip_on(False)
    ax[0].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[0], 1, loc=1)
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[0], axins, loc1=2, loc2=4, fc="b", ec="0.5")

    # fill with yellow by setting 'facecolor' field
    bbox3 = TransformedBbox(bbox, ax[1].transData)
    bbox4 = TransformedBbox(bbox, ax[2].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox3, bbox4, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", facecolor="y")
    p.set_clip_on(False)
    ax[1].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[1], 1, loc=1)
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[1], axins, loc1=2, loc2=4, facecolor="y", ec="0.5")

    # fill with green by setting 'color' field
    bbox5 = TransformedBbox(bbox, ax[2].transData)
    bbox6 = TransformedBbox(bbox, ax[3].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox5, bbox6, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", color="g")
    p.set_clip_on(False)
    ax[2].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[2], 1, loc=1)
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[2], axins, loc1=2, loc2=4, color="g", ec="0.5")

    # fill with green but color won't show if set fill to False
    bbox7 = TransformedBbox(bbox, ax[3].transData)
    bbox8 = TransformedBbox(bbox, ax[4].transData)
    # BboxConnectorPatch won't show green
    p = BboxConnectorPatch(
        bbox7, bbox8, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", fc="g", fill=False)
    p.set_clip_on(False)
    ax[3].add_patch(p)
    # marked area won't show green
    axins = zoomed_inset_axes(ax[3], 1, loc=1)
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    axins.get_xaxis().set_ticks([])
    axins.get_yaxis().set_ticks([])
    mark_inset(ax[3], axins, loc1=2, loc2=4, fc="g", ec="0.5", fill=False)


@image_comparison(baseline_images=['zoomed_axes',
                                   'inverted_zoomed_axes'],
                  extensions=['png'])
def test_zooming_with_inverted_axes():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    ax.axis([1, 3, 1, 3])
    inset_ax = zoomed_inset_axes(ax, zoom=2.5, loc=4)
    inset_ax.axis([1.1, 1.4, 1.1, 1.4])

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    ax.axis([3, 1, 3, 1])
    inset_ax = zoomed_inset_axes(ax, zoom=2.5, loc=4)
    inset_ax.axis([1.4, 1.1, 1.4, 1.1])
