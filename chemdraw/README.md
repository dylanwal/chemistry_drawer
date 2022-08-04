
# Introduction

The code is spilt into two chunks: 'chemistry objects' and 'drawer'. The chemistry objects capture all the 
details to create, store, and organize all information about the respective objects.
The Drawer objects then use the chemistry objects to draw the objects.

Global formatting is done through the `drawer.config`.

Local formatting is done through the chemistry objects.

---

## Chemistry Objects


"+" is for drawing only
```mermaid
classDiagram
    Molecule *-- Atom
    Molecule *-- Bond
    Molecule *-- Ring
    Molecule *-- Parenthesis
    
    class Molecule{
        str name
        str smiles
        list[Atom] atoms
        list[Bond] bonds
        list[Ring] rings
        list[Parenthesis] parenthesis
        np.ndarray coordinates
        np.ndarray vector
        add_parenthesis()
    }
    
    class Atom{
        int id_
        str symbol
        int number_hydrogens
        list[Bond] bonds
        list[Ring] rings
        np.ndarray coordinates
        +Font font
        +Highlight highlight
        +int number
    }
    
    class Bond{
        int id_
        BondType type_
        np.ndarray atom_ids
        BondStereoChem stereo_chem
        list[Atom] atoms
        list[Ring] rings
        np.ndarray center
        +Line line_format
        +Highlight highlight
        +int number
    }
    
    class Ring{
        int id_
        np.ndarray atom_ids
        bool aromatic
        list[Atom] atoms
        list[Bond] bonds
        int ring_size
        np.ndarray center
        +Highlight highlight
        +int number
    }
    
    class Parenthesis{
        int id_
        np.ndarray vector
        float size
        Parenthesis partner
        list[Atom] atoms
        list[Bond] contained_bonds
        list[Bond] cross_bond
        np.ndarray coordinates
        +Font sub_script_font
        +Font super_script_font
        +Line line_format
    }

```


---
## Drawer


```mermaid
classDiagram
    Drawer *-- Molecule
    Drawer *-- Config
    Config -- Layout
    Config -- DrawAtoms
    Config -- DrawBonds
    Config -- DrawParenthesis
    Config -- DrawHighlights
    Config -- DrawRingHighlights
    Config -- DrawAtomNumbers
    Config -- DrawBondNumbers
    Config -- DrawRingNumbers
    Config -- DrawDebug
    Config -- DrawTitle
    
    class Drawer{ 
        Molecule molecule
        Congif config
        str title
        draw()
        draw_img()
        draw_html()
        }
    
    class Config{
    list[str] draw_order    
    }

```
