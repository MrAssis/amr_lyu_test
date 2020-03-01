#!/usr/bin/env python3.6
# coding=utf-8
'''


                data["ner"] = []
                data["tok"] = []
                data["lem"] = []
                data["pos"] = []
                for snt_tok in snt:
                    data["ner"].append(snt_tok['ner'])
                    data["tok"].append(snt_tok['word'])
                    data["lem"].append(snt_tok['lemma'])
                    data["pos"].append(snt_tok['pos'])
data["ner"].append(snt_tok['ner'])
data["tok"].append(snt_tok['word'])
data["lem"].append(snt_tok['lemma'])
data["pos"].append(snt_tok['pos'])

Scripts to run the model to parse a file. Input file should contain each sentence per line
A file containing output will be generated at the same folder unless output is specified.
@author: Chunchuan Lyu (chunchuan.lv@gmail.com)
@since: 2018-05-30
'''

from torch import cuda
from parser.AMRProcessors import *
from src.train import read_dicts,train_parser

def generate_parser():
    parser = train_parser()
    parser.add_argument('-output', default=None)
    parser.add_argument('-with_graphs', type=int,default=1)
    parser.add_argument("-input",default=None,type=str,
                        help="""input file path""")
    parser.add_argument("-text",default=None,type=str,
                        help="""a single sentence to parse""")
    parser.add_argument("-processed",default=0,type=int,
                        help="""a single sentence to parse""")
    return parser

if __name__ == "__main__":
    global opt
    opt = generate_parser().parse_args()
    opt.lemma_dim = opt.dim
    opt.high_dim = opt.dim

    opt.cuda = len(opt.gpus)

    if opt.cuda and opt.gpus[0] != -1:
        cuda.set_device(opt.gpus[0])
    dicts = read_dicts()
    processed = opt.processed==1
    Parser = AMRParser(opt,dicts,parse_from_processed= processed)

    if opt.input:

        filepath = opt.input
        out = opt.output if opt.output else filepath+"_parsed"
        print ("processing "+filepath)
        n = 0
        processed_sentences = 0
        with open(out,'w') as out_f:
            with open(filepath,'r') as f:
                line = f.readline()
                batch = []
                while line  and line.strip() != "":
                    while line  and line.strip() != "" and len(batch) < opt.batch_size:
                        batch.append(line.strip())
                        line = f.readline()

                    output = Parser.parse_batch(batch)
                    for snt, others in zip(batch,output):
                        out_f.write("# ::snt "+snt+"\n")
                        out_f.write(others)
                        out_f.write("\n")
                    processed_sentences = processed_sentences + len(batch)
                    print ("processed_sentences" , processed_sentences)
                    batch = []
        print ("done processing "+filepath)
        print (out +" is generated")

    elif opt.input:
        filepath = opt.input
        out = opt.output if opt.output else filepath+"_parsed"
        print ("processing "+filepath)
        n = 0
        with open(out,'w') as out_f:
            with open(filepath,'r') as f:
                line = f.readline()
                while line != '' :
                    if line.strip() != "":
                        output = Parser.parse_batch([line.strip()])
                        out_f.write("# ::snt "+line)
                        out_f.write(output[0])
                        out_f.write("\n")
                    line = f.readline()
        print ("done processing "+filepath)
        print (out +" is generated")
    elif opt.text:
        output = Parser.parse_one(opt.text)
        print ("# ::snt "+opt.text)
        for i in output:
            print (i)
    else:
        print ("option -input [file] or -text [sentence] is required.")
