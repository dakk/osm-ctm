import json
import os
import sys


__AUTHOR__ = "Davide Gessa"


class CtmToOsm:
	VERSION = 1
	
	def __init__ (self):
		fj = open ('json/ctm.json', 'r')
		fgj = open ('json/ctm_geo.json', 'r')
		
		self.jctm = json.load (fj);
		self.jctmgeo = json.load (fgj)
		
		fj.close ()
		fgj.close ()
		
		
	def generate (self, out):
		nodeid = 1
		f = open (out, 'w')
		
		# Genera un dictionary | stop['H2B4'] = { id, lat, long, name }
		stops = {}
		for stop in self.jctmgeo ['coord']:
			stops [stop ['code']] = {}
			stops [stop ['code']]['lat'] = stop['lat']
			stops [stop ['code']]['lon'] = stop['lon']
			stops [stop ['code']]['id'] = nodeid
			nodeid += 1
			
			for line in self.jctm ['lines']:
				for direc in line ['directions']:
					for stop2 in direc ['stops']:
						if stop2 ['code'] == stop ['code']:			
							stops [stop ['code']]['name'] = stop2 ['name']	

				
		# Aggiungo gli id dei noid a jcm
		for line in self.jctm ['lines']:
			for direc in line ['directions']:
				for stop in direc ['stops']:
					code = stop ['code']
					stop ['id'] = stops [code]['id']
		
		
		# Genero l'osmxml		
		f.write ("<?xml version='1.0' encoding='UTF-8'?>\n")
		f.write ("<osm version='0.6' generator='ctm2osm.py'>\n")
		
		# Aggiungo le fermate come nodi
		for sk in stops:
			stop = stops[sk]
			node = "<node id='"+str (stop ['id'])+"' visible='true' lat='"+stop ['lat']+"' lon='"+stop ['lon']+"'"
			node += " version='"+str (self.VERSION)+"' highway='bus_stop' bus='yes' operator='CTM Spa'"
			node += " name='"+stop ['name']+"'" 
			node += "></node>"
					
			f.write ('\t'+node+'\n')
			
			
		# Aggiungo le bus tracks
		# http://wiki.openstreetmap.org/wiki/Buses#Services
		
		
		# Aggiungo le relations
		for line in self.jctm ['lines']:
			for direc in line ['directions']:
				# user="kmvar" uid="56190" changeset timestamp direction
				nodeid += 1
				rel = "\t<relation id='"+str (nodeid)+"' visible='true' version='"+str (self.VERSION)+"'>\n"
				
				for stop in direc ['stops']:
					ss = stops [stop['code']]
					rel += '\t\t<member type="node" ref="'+str (ss['id'])+'" role=""/>\n'
					
				rel += '\t\t<tag k="name" v="'+line['name']+'"/>\n'
				#rel += '\t\t<tag k="network" v="VVW"/>
				rel += '\t\t<tag k="operator" v="CTM Spa"/>\n'
				rel += '\t\t<tag k="route" v="bus"/>\n'
				rel += '\t\t<tag k="type" v="route"/>\n'
				rel += '\t</relation>\n'
				#  <tag k="ref" v="123"/>
				
				f.write (rel)
				
		f.write ("</osm>")
		f.close ()
		
if __name__ == "__main__":
	cto = CtmToOsm ()
	cto.generate ('osm/ctm.osm')
