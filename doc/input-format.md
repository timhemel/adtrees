# Input format

Attack-defense trees can be specified in YAML. Elements can be:

* node: description of the node
* external: makes this node point to an external tree
* or: gets a list of child nodes to make this an 'or' node. Requires a list.
* and: gets a list of child nodes to make this an 'and' node. Requires a list.
* counter: whatever node is below this field, they will be the counterpart of the current node. I.e. attack will become defense and vice versa. Can only have one node.

Example:

```
node: Top goal
or:
	- node: subgoal 1
          and:
		- node: attack step 1
		- node: attack step 2
		- node: attack step 3
	- node: subgoal 2
	  counter:
		node: countermeasures
		or:
			- node: countermeasure 1
			- node: countermeasure 2
```


