====Fiber Assignment by Continuous Tracking====

The tool employed for fiber tractography is [[http://web4.cs.ucl.ac.uk/research/medic/camino/pmwiki/pmwiki.php?n=Man.track|Camino's track]]. This tool was developed based on the FACT algorithm published by [[http://onlinelibrary.wiley.com/doi/10.1002/1531-8249(199902)45:2%3C265::AID-ANA21%3E3.0.CO;2-3/abstract|Susumu Mori et al.]] in 1999.

Let the set of voxels in the brain be $\textbf{x} = (x_i, ... , x_n)$.\\
Let the diffusion tensors at each voxel be represented by $D(x_i) = (\lambda_{1,i}, \lambda_{2,i}, \lambda_{3,i}), \forall i=[n_W \times n_L \times n_H]$, where $\lambda_{j,i}$ are principal components of the tensors..\\
Let the neighborhood of a given voxel be $\mathcal{N}(v_i) = \{ v_j : v_i \sim v_j\}, n_b=\lvert \mathcal{N}(v_i) \rvert$.\\
Let the number of all in-brain voxels be $N = [n_W] \times [n_L] \times [n_H]$.\\
Let diffusion tensor principal components be ordered such that $\lambda_{1,i} \geq \lambda_{2,i} \geq \lambda_{3,i}$.\\
Let the unit vector of local flow be $v_{\lambda_{1,i}} = \lambda_{1,i}$ $/$ $\lvert \lambda_{1,i} \rvert $.

**Inputs**: diffusion tensor image $D(\textbf{x}) \in \mathscr{D} = \{\lambda_1, \lambda_2, \lambda_3 \}^{N}$, anisotropy threshold $\epsilon \in (0,1)$

**Outputs**: fibers $f \in \mathscr{F} = \{ \mathscr{P}(S) ; S = \{ x, y, z \}^N \}$.

  - **for (**$i \in N$**)**
    - Initialize location on fiber $y_i^{(q)} = x_i$
    - Initialize empty fiber $f_i^{(q)} = \{\emptyset \}$
    - Compute continuity $R^{(q)} = \sum\limits_{j \in \mathcal{N}(y_i^{(q)})}^{n_b} \lvert v_{\lambda_{1,i}} - v_{\lambda_{1,j}} \rvert$ / $ n_b (n_b - 1)$
    - **while (**$R \geq \epsilon$**)**
      - Add position to fiber $f_i^{(q+1)} = \{ f_i^{(q)}, y_i^{(q)} \}$
      - Update location on fiber $y_i^{(q)} = y_i^{(q)} + v_{\lambda_{1,i}}$
      - Compute continuity $R^{(q)} = \sum\limits_{j \in \mathcal{N}(y_i^{(q)})}^{n_b} \lvert v_{\lambda_{1,i}} - v_{\lambda_{1,j}} \rvert$ / $ n_b (n_b - 1)$
    - **end while**
  - **end for**
