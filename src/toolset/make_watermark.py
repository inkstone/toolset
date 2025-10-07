import glob
import shutil
import os
import argparse
import sys
from importlib import resources
sys.setrecursionlimit(15000)

from pypdf.constants import DocumentInformationAttributes
from pypdf import PdfReader, PdfWriter, Transformation

def get_stamps(stamp_files) :
    ret = list()
    for f in stamp_files :
        io = resources.files("toolset.data").joinpath(f + ".pdf").open("rb")
        p = PdfReader(io).pages[0]
        w = p.cropbox.width
        h = p.cropbox.height
        ret.append((p, w, h))
    return ret

stamp_files = ['pheonix', 'dragon', 'paw']
ratio = 0.7
num_skip = 1

def debug_page(page):
    print(page.cropbox)
    print(page.mediabox)
    print(page.trimbox)
    print(page.artbox)


def do_convert(filein, fileout, stamps, **kw):
    writer = PdfWriter(clone_from=filein)
    for i, page in enumerate(writer.pages):
        if i >= kw.get('skip',1):
            width = page.cropbox.width
            height = page.cropbox.height
            left = page.cropbox.left
            bottom = page.cropbox.bottom

            stamp = stamps[(i-num_skip)%len(stamps)]
            scale = width * kw.get('ratio', 0.7) / stamp[1]
            dx = (width - stamp[1] * scale)/2 + left
            dy = (height - stamp[2] * scale)/2 + bottom
            trans = Transformation().scale(scale).translate(dx, dy)
            page.merge_transformed_page(stamp[0], trans, over=kw.get('over', False))  # here set to False for watermarking

    writer.write(fileout)

def convert(filesin, directory, stamps, **kw) :
    for filein in filesin:
        filename = os.path.basename(filein)
        print("Converting %s" % filename)
        do_convert(filein, directory + '/' + filename, stamps, **kw)

def main():
    parser = argparse.ArgumentParser(description="Add watermarks in Given PDF file(s)")
    parser.add_argument("input", type=str, help = 'input file or directory')
    parser.add_argument('--over', default=False, action='store_true', help='put watermark on top of original page')
    parser.add_argument('--skip', type = int, default = 1, help='Skip first several pages for watermark')
    parser.add_argument('--ratio', type = float, default=0.7, help='Scaling ratio of the watermark')

    args = parser.parse_args()
    opt = dict()
    if os.path.isdir(args.input) :
        path = os.path.expanduser(args.input)
        files = glob.glob(path + '/*.pdf')
    else:
        path = os.path.dirname(args.input)
        files = [args.input]
    opt['skip'] = args.skip
    opt['over'] = args.over
    opt['ratio'] = args.ratio
    output_dir = path + '/output'
    os.makedirs(output_dir, exist_ok=True)
    stamps = get_stamps(stamp_files)
    convert(files, output_dir, stamps, **opt)
    print('Convert files successfully. Please find the result at %s' % os.path.abspath(output_dir))

if __name__ == '__main__' :

    main()

#stamps = get_stamps(stamp_files)
#do_convert('FAT.pdf', 'FAT_m.pdf', stamps)
