Paginador = function(divPaginador, tabla, tamPagina){

  this.miDiv = divPaginador; //un DIV donde irán controles de paginación
  this.tabla = tabla;           //la tabla a paginar
  this.tamPagina = tamPagina; //el tamaño de la página (filas por página)
  this.pagActual = 1;         //asumiendo que se parte en página 1
  this.paginas = Math.floor((this.tabla.rows.length - 1) / this.tamPagina); //¿?

  this.SetPagina = function(num){

    if(num == 1)
      document.getElementById('pag_ant').className = 'tope';

    if(num == this.paginas)
      document.getElementById('pag_sig').className = 'tope';

    if (num < 0 || num > this.paginas)
      return;

    this.pagActual = num;
    document.getElementById('pag_num_id').innerHTML = num + ' de ' + this.paginas;
    var min = 1 + (this.pagActual - 1) * this.tamPagina;
    var max = min + this.tamPagina - 1;

    for(var i = 1; i < this.tabla.rows.length; i++){

      if (i < min || i > max)
          this.tabla.rows[i].style.display = 'none';
      else
          this.tabla.rows[i].style.display = '';
    }
    this.miDiv.firstChild.rows[0].cells[1].innerHTML = this.pagActual  + ' de ' + this.paginas;
}

this.Mostrar = function(){

    // var combo = document.getElementById('paginas');
    //
    // var p = document.createElement('option');
    // p.value = this.tabla.rows.length;
    // p.innerHTML = this.tabla.rows.length;
    // combo.options.add(p);

    //Crear la tabla
    var tblPaginador = document.createElement('table');
    tblPaginador.id = 'tblPaginador';
    tblPaginador.style.width = '20%';

    //Agregar una fila a la tabla
    var fil = tblPaginador.insertRow(tblPaginador.rows.length);

    //Ahora, agregar las celdas que serán los controles
    var ant = fil.insertCell(fil.cells.length);
    ant.innerHTML = '← Anterior';
    ant.className = 'tope'; //con eso le asigno un estilo
    ant.id = 'pag_ant';
    var self = this;

    ant.onclick = function(){
      if (self.pagActual == 1)
          return;

      document.getElementById('pag_sig').className = 'pag_btn';
      self.SetPagina(self.pagActual - 1);
    }

    var num = fil.insertCell(fil.cells.length);
    num.innerHTML = self.pagActual + ' de ' + self.paginas; //en rigor, aún no se el número de la página
    num.id = 'pag_num_id';
    num.align = 'center';
    num.className = 'pag_num';

    var sig = fil.insertCell(fil.cells.length);
    sig.innerHTML = 'Siguiente →';
    sig.className = 'pag_btn';
    sig.align = 'right';
    sig.id = 'pag_sig';

    sig.onclick = function(){
      if (self.pagActual == self.paginas)
          return;

      document.getElementById('pag_ant').className = 'pag_btn';
      self.SetPagina(self.pagActual + 1);
    }

    //Como ya tengo mi tabla, puedo agregarla al DIV de los controles
    this.miDiv.appendChild(tblPaginador);

    //¿y esto por qué?
    if (this.tabla.rows.length - 1 > this.paginas * this.tamPagina)
      this.paginas = this.paginas + 1;

    this.SetPagina(this.pagActual);
  }
}
