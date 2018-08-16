#!/usr/bin/env python

import re
import yaml

class ADTreeParser:
    def __init__(self):
        pass
    def parse(self,inp):
        data = yaml.load(inp)
        return data

class ADTreeRenderer:
    def __init__(self):
        pass
    def render(self,data):
        pass

class ADTreeBlockdiagRenderer(ADTreeRenderer):
    fontheight = 11
    fontwidth = 9
    def render(self,data):
        self.result = ""
        self.renderGraphBegin()
        self.renderNode(data,[0])
        self.renderGraphEnd()
        return self.result
    def renderGraphBegin(self):
        self._out("blockdiag {")
        # self._out("orientation=portrait;")
        # self._out("default_fontfamily=arial;")
    def renderGraphEnd(self):
        self._out("}")
    def getNodeId(self,path):
        return "n"+"_".join(map(str,path))
    def renderNode(self,data,path,adstate=False):
        """data is the data structure,
        path is the tree path id,
        adstate is a boolean indicating attack or defense node
        """
        nodeid = self.getNodeId(path)
        node_attrs = {}
        if adstate:
            node_attrs['shape'] = 'box'
            node_attrs['linecolor'] = 'green'
        else:
            node_attrs['shape'] = 'ellipse'
            node_attrs['linecolor'] = 'red'
        node_attrs['label'] = '"%s"' % data.get('node','').replace('\\','\\\\').replace('"','\\"')
        width,height = self.getBoxSize(data.get('node',''))
        node_attrs['height'] = height * self.fontheight + 35
        node_attrs['width'] = width * self.fontwidth + 10
        if data.get('external'):
            node_attrs['shape'] = 'roundedbox'
            # node_attrs['style'] = 'filled'
            node_attrs['color'] = 'lightgrey'
        self.renderGraphNode(nodeid,**node_attrs)
        name = data['node']
        ornodes = data.get('or',[])
        if ornodes:
            ors = self.renderNodelist(ornodes,path,0,adstate)
            ornodeids = [ self.getNodeId(path+[i]) for i in range(len(ornodes)) ]
            self.renderGraphEdges(nodeid, ornodeids,dir='none')
        andnodes = data.get('and',[])
        ands = self.renderNodelist(andnodes,path,len(ornodes), adstate)
        if andnodes:
            andnodeid = nodeid+'_and'
            if adstate:
                color = 'green'
            else:
                color = 'red'
            # self.renderGraphNode(andnodeid,shape='diamond',label='"&"', textcolor=color)
            # self.renderGraphEdges(nodeid,[andnodeid],dir='none')
            andnodeids = [ self.getNodeId(path+[len(ornodes)+i]) for i in range(len(andnodes)) ]
            self.renderGraphEdges(nodeid,andnodeids,dir='back',hstyle='aggregation')
        counternode = data.get('counter')
        if counternode:
            counter = self.renderNode(counternode,path+[ len(ornodes)+len(andnodes) ], not adstate)
            counternodeid = self.getNodeId(path+[len(ornodes)+len(andnodes)])
            self.renderGraphEdges(nodeid, [counternodeid],style='dotted',dir='none')

    def renderGraphNode(self,nodeid,**kwargs):
        options = ""
        if kwargs:
            options = "[ %s ]" % ",".join("%s=%s"% (k,v) for k,v in kwargs.items())
        self._out('%s %s;' % (nodeid,options))
    def renderNodelist(self,datas,path,offset,adstate):
        for i in range(len(datas)):
            self.renderNode(datas[i], path+[offset+i],adstate)
    def renderGraphEdges(self,srcnodeid,dstnodeids,**kwargs):
        dstnodelist = ", ".join(dstnodeids)
        attrstring = ""
        if kwargs:
            attrstring = "[ %s ]" % ",".join("%s=%s"% (k,v) for k,v in kwargs.items())
        self._out("%s -> %s %s;" % (srcnodeid, dstnodelist, attrstring))
    def _out(self,line):
        self.result += line+"\n"
    def getBoxSize(self,text):
        lines = text.splitlines()
        height = len(lines)
        width = max([len(l) for l in lines])
        return width,height


class ADTreeGraphvizRenderer(ADTreeRenderer):
    def render(self,data):
        self.result = ""
        self.renderGraphBegin()
        self.renderNode(data,[0])
        self.renderGraphEnd()
        return self.result
    def renderGraphBegin(self):
        self._out("graph G {")
        self._out("rankdir=LR;")
        # self._out("splines=ortho;")
    def renderGraphEnd(self):
        self._out("}")
    def getNodeId(self,path):
        return "n"+"_".join(map(str,path))
    def renderString(self,s):
        s= s.replace('\\','\\\\') \
            .replace('"','\\"') \
            .replace('\n','\\n') \
            .replace('}','\\}') \
            .replace('{','\\{') \
            .replace('|','\\|')
        return s
    def renderNode(self,data,path,adstate=False):
        """data is the data structure,
        path is the tree path id,
        adstate is a boolean indicating attack or defense node
        """
        # print >>sys.stderr, "# %s %s %s" % (data,path,adstate)
        # print >>sys.stderr, "# %s"  % type(data), type({})
        if type(data) != type({}):
            raise Exception("Invalid data structure: %s" % data)
        nodeid = self.getNodeId(path)
        node_attrs = {}
        ornodes = data.get('or',[])
        andnodes = data.get('and',[])
        if adstate:
            node_attrs['shape'] = 'record'
            node_attrs['color'] = '"#087f20"'
            node_attrs['style'] = 'filled'
            node_attrs['fillcolor'] = '"#81c68f"'
        else:
            node_attrs['shape'] = 'Mrecord'
            node_attrs['color'] = '"#7f0808"'
            node_attrs['style'] = 'filled'
            node_attrs['fillcolor'] = '"#d38181"'
        if andnodes:
            node_attrs['label'] = '"{ <f> %s | <and> &}"' % self.renderString(data.get('node',''))
        else:
            node_attrs['label'] = '" <f> %s"' % self.renderString(data.get('node',''))
        if data.get('external'):
            # node_attrs['shape'] = 'ellipse'
            node_attrs['style'] = 'filled'
            node_attrs['fillcolor'] = 'lightgrey'
        self.renderGraphNode(nodeid,**node_attrs)
        name = data['node']
        ors = self.renderNodelist(ornodes,path,0,adstate)
        for i in range(len(ornodes)):
            subnodeid = self.getNodeId(path+[ i ])
            self.renderGraphEdge(nodeid,subnodeid)
        ands = self.renderNodelist(andnodes,path,len(ornodes), adstate)
        if andnodes:
            andnodeid = nodeid+'_and'
            if adstate:
                color = 'green'
            else:
                color = 'red'
            # self.renderGraphNode(andnodeid,shape='diamond',label='"&"', color=color)
            andnodeid = nodeid+':and'
            # self.renderGraphEdge(nodeid,andnodeid,len=0.02)
            for i in range(len(andnodes)):
                subnodeid = self.getNodeId(path+[ len(ornodes) + i ])
                self.renderGraphEdge(andnodeid,subnodeid)
                # self.renderGraphEdge(andnodeid,subnodeid,arrowtail='crow',dir='back',sametail=andnodeid)
        counternode = data.get('counter')
        if counternode:
            counter = self.renderNode(counternode,path+[ len(ornodes)+len(andnodes) ], not adstate)
            counternodeid = self.getNodeId(path+[len(ornodes)+len(andnodes)])
            self.renderGraphEdge(nodeid+":f", counternodeid,style='dotted')

    def renderNodelist(self,datas,path,offset,adstate):
        for i in range(len(datas)):
            self.renderNode(datas[i], path+[offset+i],adstate)
    def renderGraphNode(self,nodeid,**kwargs):
        options = ""
        if kwargs:
            options = "[ %s ]" % ",".join("%s=%s"% (k,v) for k,v in kwargs.items())
        self._out('%s %s;' % (nodeid,options))
    def renderGraphEdge(self,nodeFrom,nodeTo,**kwargs):
        options = ""
        if kwargs:
            options = "[ %s ]" % ",".join("%s=%s"% (k,v) for k,v in kwargs.items())
        self._out("%s -- %s %s" % (nodeFrom,nodeTo,options))
    def _out(self,line):
        self.result += line+"\n"


if __name__=="__main__":
    import sys
    t = ADTreeParser().parse(sys.stdin)
    r = ADTreeGraphvizRenderer()
    # r = ADTreeBlockdiagRenderer()
    print r.render(t)
