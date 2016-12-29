for i in `ls $1`
	do
	sudo python -c "import networkx as nx; g = nx.read_gpickle('$1/$i'); nx.write_graphml(g,'`echo $1/graphml/$i | cut -d '.' -f 1`.graphml')"
	echo $i
done
