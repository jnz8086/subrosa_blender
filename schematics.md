
# Format schematics

## .cmo

```c
{
    int CMod;
    int version;
	
	int vertex_count;
	struct vertex{
		
		version == 3:
			
			float x,y,z;
			float u,v;
			float unknown; //(always 0)
		
		version < 3:
		
			float x,y,z;
			float unknown;
		
	} vertices[vertex_count];
	
	int face_count;
	struct face{
		
		int face_verts_count; //can be 3 or 4
		int face_verts[face_verts_count];
		
		version > 1:
			int unknown;
		
		int material_id; //e.g. heli windshield
		
	} faces [face_count];
	
}
```

## .cmc

```c
{
	int CMod;
	int version;
	
	int bone_count;
	struct bone{
		float position[3]; //seem to be in some kind of local coordinates
	} bones[bone_count]
	
	int vertex_count;
	struct vertex{
		
		float x,y,z;
		
		struct bone_weight{
			float offset[3];
			float weight;
		} bone_weights[bone_count];
		
		float u,v;
		
	}[vertex_count]
	
	int face_cnt;
	struct face{
	   int face_verts[3];
	} faces[face_cnt];
}
```

## .itm

```c
{
	int version;
	
	//todo
	float unknown[6];
	
	//todo
	int unknown_points_count;
	struct unknown_point{
		int id;
		float x,y,z;
	} unknown_points[unknown_points_count];
	
	int vertex_count;
	struct vertex{
		float pos[3];
		float uv[2];
	}[vertex_count]
	
	int face_cnt;
	struct face{
		int face_verts_count;
		int face_verts[face_verts_count];
	} faces[face_cnt];
	
}
```
