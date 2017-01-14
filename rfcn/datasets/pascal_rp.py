import cv2
import fcn
import numpy as np
import skimage.color

from rfcn.datasets.pascal import PascalInstanceSegmentationDataset
from rfcn import utils


class PascalInstanceSegmentationRPDataset(PascalInstanceSegmentationDataset):

    """Pascal VOC2012 instance segmentation dataset with region proposals"""

    def get_example(self, i):
        datum, lbl_cls, lbl_ins = \
            super(PascalInstanceSegmentationRPDataset, self).get_example(i)
        # get rois
        img = self.datum_to_img(datum)
        datum = self.img_to_datum(img)
        rois = utils.get_region_proposals(img)
        roi_clss, _ = utils.label_rois(rois, lbl_ins, lbl_cls)
        samples = utils.get_positive_negative_samples(roi_clss != 0)
        rois = rois[samples]
        return datum, lbl_cls, lbl_ins, rois

    def visualize_example(self, i):
        datum, lbl_cls, lbl_ins, rois = self.get_example(i)
        img = self.datum_to_img(datum)
        rois_clss, _ = utils.label_rois(rois, lbl_ins, lbl_cls)
        colors = fcn.utils.labelcolormap(len(self.class_names))

        # visualize label
        lbl_ins[lbl_cls == 0] = -1
        viz_lbl = skimage.color.label2rgb(lbl_ins, img)
        viz_lbl = (viz_lbl * 255).astype(np.uint8)
        ins_clss, boxes = utils.label2instance_boxes(
            lbl_ins, lbl_cls, ignore_class=(-1, 0))
        viz_lbl = utils.draw_instance_boxes(
            viz_lbl, boxes, ins_clss,
            n_class=len(self.class_names),
            captions=self.class_names[ins_clss])

        # visualize rois
        viz_all = viz_lbl.copy()
        viz_pos = viz_lbl.copy()
        for roi, roi_cls in zip(rois, rois_clss):
            x1, y1, x2, y2 = roi
            color = (colors[roi_cls][::-1] * 255).astype(np.uint8).tolist()
            cv2.rectangle(viz_all, (x1, y1), (x2, y2), color)
            if roi_cls != 0:
                cv2.rectangle(viz_pos, (x1, y1), (x2, y2), color)

        return fcn.utils.get_tile_image([viz_lbl, viz_all, viz_pos], (1, 3))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    dataset = PascalInstanceSegmentationRPDataset('val')
    for i in xrange(len(dataset)):
        img_viz = dataset.visualize_example(i)
        plt.imshow(img_viz)
        plt.show()
