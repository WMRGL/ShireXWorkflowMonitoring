document.addEventListener("DOMContentLoaded", function() {
    var dropdowns = document.querySelectorAll('.navbar .dropdown');

    dropdowns.forEach(function(dropdown) {
        dropdown.addEventListener('mouseenter', function() {
            var menu = this.querySelector('.dropdown-menu');
            menu.classList.remove('show'); // Reset the animation - MW
            setTimeout(function() { // Reapply the class after a short delay - MW
                menu.classList.add('show');
            }, 10);
        });

        dropdown.addEventListener('mouseleave', function() {
            this.querySelector('.dropdown-menu').classList.remove('show');
        });
    });


    const darkModeToggle = document.getElementById('dark-mode-toggle'); // Corrected method name
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            const isDarkMode = this.checked;
            document.body.classList.toggle('dark-mode', isDarkMode);
            localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
            applyDarkModeStyles(isDarkMode);
        });

        // Apply user preferences on page load
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }
        applyDarkModeStyles(isDarkMode);
    }

    document.getElementById('btnClose').addEventListener('click', function () { DoClose(); } );

        function DoClose() {
            window.close()
        }

    // Function to apply dark or light mode styles
    function applyDarkModeStyles(isDarkMode) {
        if (isDarkMode) {
            document.body.style.backgroundColor = '#595352';
            document.body.style.color = '#fff';
        } else {
            document.body.style.backgroundColor = '#ffffff';
            document.body.style.color = '#000';
        }
    }
});


// Get the modal - MW
var modal = document.getElementById("font-size-modal");

// Get the button that opens the modal - MW
var btn = document.getElementById("settings-btn");

// Get the <span> element that closes the modal - MW
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal - MW
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal - MW
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it - MW
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// Function to change font size - MW
function changeFontSize(size) {
  var body = document.body;
  if(size === 'small') {
    body.style.fontSize = '12px';
  } else if(size === 'medium') {
    body.style.fontSize = '16px'; // This is typically the default size - MW
  } else if(size === 'large') {
    body.style.fontSize = '20px';
  }

  localStorage.setItem('preferredFontSize', size); // Stores the font size in local storage - MW
  modal.style.display = "none"; // Close the modal after selection - MW
}

function changeFontStyle(){
    var selectedFont = document.getElementById('font-style-select').value;
    document.documentElement.style.setProperty('--font-family', selectedFont);
    localStorage.setItem('selectedFontStyle', selectedFont);
}

function applySavedFontSize(){
    var savedSize = localStorage.getItem('preferredFontSize');
    if(savedSize){
        changeFontSize(savedSize);
    }
}
// Call applySavedFontSize when the page loads - MW
document.addEventListener('DOMContentLoaded', applySavedFontSize);
document.addEventListener('DOMContentLoaded', (event) => {
    var selectedFont = localStorage.getItem('selectedFontStyle');
    if(selectedFont){
        document.documentElement.style.setProperty('--font-family', selectedFont);
        document.getElementById('font-style-select').value = selectedFont;
    }
})


window.addEventListener('load', function() {
            document.getElementById('txtPageNumber').value = '1';
        })

        document.getElementById('ddlCriteriaDiseaseIndication1').addEventListener('change', function () {

            if (IsFormValid()) {
                document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value = '';
                DoPostBack();
            }
        } )

        document.getElementById('ddlCriteriaDiseaseIndication2').addEventListener('change', function () {
            if (IsFormValid()) {
                document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value = '';
                DoPostBack();
            }
        } )

        document.getElementById('ddlCriteriaDiseaseIndication3').addEventListener('change', function () {
            if (IsFormValid()) {
                document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value = '';
                document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value = '';
                DoPostBack();
            }
        } )

        document.getElementById('btnPageFirst').addEventListener('click', function () { DoSubmitFirstPage(); } );
        document.getElementById('btnPagePrevious').addEventListener('click', function () { DoSubmitPreviousPage(); } );
        document.getElementById('btnPageNext').addEventListener('click', function () { DoSubmitNextPage(); } );
        document.getElementById('btnPageLast').addEventListener('click', function () { DoSubmitLastPage(); } );

        function DoPostBack() {
            document.getElementById('formSearch').submit();
        }

        function DoSubmitFirstPage() {
            _pageNumber = document.getElementById('txtPageNumber');
            _pageNumber.value = '1';

            document.getElementById('formSearch').submit();
        }

        function DoSubmitPreviousPage() {
            var _pageNumber = document.getElementById('txtPageNumber');
            if (workflowCases != null) {
                if (workflowCases.has_previous) {
                    _pageNumber.value = workflowCases.previous_page_number;
                } else {
                    _pageNumber.value = '1';
                }
            } else {
                _pageNumber.value = '1';
            }
            document.getElementById('formSearch').submit();
        }


        function DoSubmitNextPage()
        {
            var _pageNumber = document.getElementById('txtPageNumber');
            if (workflowCases != null) {
                if (workflowCases.has_next) {
                    _pageNumber.value = workflowCases.next_page_number;
                } else {
                    _pageNumber.value = '1';
                }
            } else {
                _pageNumber.value = '1';
            }
            document.getElementById('formSearch').submit();
        }


        function DoSubmitLastPage() {
            var _pageNumber = document.getElementById('txtPageNumber');

            if (workflowCases != null) {
                if (workflowCases.has_next) {
                    _pageNumber.value = "10"; // assuming workflowCases.paginator.num_pages is 10
                } else {
                    _pageNumber.value = '1';
                }
            } else {
                _pageNumber.value = '1';
            }
            document.getElementById('formSearch').submit();
        }

        function IsFormValid() {

            let _retVal = true
            let _errorMessage = ''

            let _indicationDisease1 = Nz(document.getElementById('ddlCriteriaDiseaseIndication1').value,'');
            let _indicationDisease2 = Nz(document.getElementById('ddlCriteriaDiseaseIndication2').value,'');
            let _indicationDisease3 = Nz(document.getElementById('ddlCriteriaDiseaseIndication3').value,'');

            let _reason1 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value,'');
            let _reason2 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value,'');
            let _reason3 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value,'');

            if (_indicationDisease2 != '' && _indicationDisease1 == '')
            {
                _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
            }
            else
            {
                if (_indicationDisease3 != '' && _indicationDisease1 == '')
                {
                    _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
                }
                else
                {
                    if (_indicationDisease3 != '' && _indicationDisease2 == '')
                    {
                        _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
                    }
                }
            }

            if (_reason2 != '' && _reason1 == '')
            {
                _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
            }
            else
            {
                if (_reason3 != '' && _reason1 == '')
                {
                    _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
                }
                else
                {
                    if (_reason3 != '' && _reason2 == '')
                    {
                        _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
                    }
                }
            }

            if (_errorMessage != '') {
                _retVal = false;
                window.alert(_errorMessage);
            }

            return _retVal;
        }

        function Nz (_object, _defaultValue) {
            if (_object == null || _object == undefined)
            {
                _object = _defaultValue;
            }
            return _object
        }


        function DoClaim(labno) {
        if (!labno) {
            console.error("labno is null or undefined");
            return;
        }

        console.log("labno:", labno); // Log the labno to ensure it is correct

        let workflowName = 'RAML'; // Replace with actual logic if needed
        let url = `/Molecular/Allocate/${labno}/${workflowName}/AllocateComplete/`;
        console.log("Navigating to URL:", url); // Debugging
        window.location.href = url;
    }


        function SortTable(n){
            //Doing it this way means it can only sort what's on the screen, but it'll reduce the SQL sproc calls #}
           var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
           table = document.getElementById("ResultsTable");
           switching=true;
           dir = "asc";
           while(switching){
               switching = false;
               rows = table.rows;
               for (i=1; i < rows.length-1; i++){
                   shouldSwitch = false;
                   x = rows[i].getElementsByTagName("TD")[n];
                   y = rows[i+1].getElementsByTagName("TD")[n];
                   if (dir == "asc"){
                       if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()){
                           shouldSwitch = true;
                           break;
                       }
                   }else if (dir="desc"){
                       if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()){
                           shouldSwitch = true;
                           break;
                       }
                   }
               }
               if(shouldSwitch){
                   rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
                   switching = true;
                   switchcount++;
               }else{
                   if(switchcount==0 && dir == "asc"){
                       dir = "desc";
                       switching = true;
                   }
               }
           }
        }

        document.addEventListener("DOMContentLoaded", function() {
        var dropdowns = document.querySelectorAll('.navbar .dropdown');

        dropdowns.forEach(function(dropdown) {
            dropdown.addEventListener('mouseenter', function() {
                var menu = this.querySelector('.dropdown-menu');
                menu.classList.remove('show'); // Reset the animation - MW
                setTimeout(function() { // Reapply the class after a short delay - MW
                    menu.classList.add('show');
                }, 10);
            });

            dropdown.addEventListener('mouseleave', function() {
                this.querySelector('.dropdown-menu').classList.remove('show');
            });
        });


        const darkModeToggle = document.getElementById('dark-mode-toggle'); // Corrected method name
        if (darkModeToggle) {
            darkModeToggle.addEventListener('change', function() {
                const isDarkMode = this.checked;
                document.body.classList.toggle('dark-mode', isDarkMode);
                localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
                applyDarkModeStyles(isDarkMode);
            });

            // Apply user preferences on page load
            const isDarkMode = localStorage.getItem('darkMode') === 'true';
            if (isDarkMode) {
                document.body.classList.add('dark-mode');
                darkModeToggle.checked = true;
            }
            applyDarkModeStyles(isDarkMode);
        }

        // Function to apply dark or light mode styles
        function applyDarkModeStyles(isDarkMode) {
            if (isDarkMode) {
                document.body.style.backgroundColor = '#595352';
                document.body.style.color = '#fff';
            } else {
                document.body.style.backgroundColor = '#ffffff';
                document.body.style.color = '#000';
            }
        }
    });


    // Get the modal - MW
    var modal = document.getElementById("font-size-modal");

    // Get the button that opens the modal - MW
    var btn = document.getElementById("settings-btn");

    // Get the <span> element that closes the modal - MW
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal - MW
    btn.onclick = function() {
        console.log("Settings button clicked");
      modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal - MW
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it - MW
    window.onclick = function(event) {
        console.log("Close button clicked")
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }

    // Function to change font size - MW
    function changeFontSize(size) {
      var body = document.body;
      if(size === 'small') {
        body.style.fontSize = '12px';
      } else if(size === 'medium') {
        body.style.fontSize = '16px'; // This is typically the default size - MW
      } else if(size === 'large') {
        body.style.fontSize = '20px';
      }

      localStorage.setItem('preferredFontSize', size); // Stores the font size in local storage - MW
      modal.style.display = "none"; // Close the modal after selection - MW
    }

    function changeFontStyle(){
        // Selects the font from the list - MW
        var selectedFont = document.getElementById('font-style-select').value;
        document.documentElement.style.setProperty('--font-family', selectedFont);
        localStorage.setItem('selectedFontStyle', selectedFont);

        var isDyslexiaAidChecked = document.getElementById('dyslexia-checkbox').checked;

        if(isDyslexiaAidChecked) {
            document.body.style.letterSpacing = "5px";
            document.body.style.wordSpacing = "35px";
            document.body.classList.add('dyslexic');
        }else{
            document.body.classList.remove('dyslexic');
        }
        localStorage.setItem('isDyslexiaAidChecked', isDyslexiaAidChecked);
    }

    function applySavedFontSize(){
        // Applies these fonts to the page
        var savedSize = localStorage.getItem('preferredFontSize');
        if(savedSize){
            changeFontSize(savedSize);
        }
    }
    // Call applySavedFontSize when the page loads - MW
    document.addEventListener('DOMContentLoaded', applySavedFontSize);
    document.addEventListener('DOMContentLoaded', (event) => {
        var selectedFont = localStorage.getItem('selectedFontStyle');
        if(selectedFont){
            document.documentElement.style.setProperty('--font-family', selectedFont);
            document.getElementById('font-style-select').value = selectedFont;
        }

        var isDyslexiaAidChecked = localStorage.getItem('isDyslexiaAidChecked') === 'true';
        if (isDyslexiaAidChecked) {
            document.body.classList.add('dyslexic');
        } else {
            document.body.classList.remove('dyslexic');
        }
        document.getElementById('dyslexia-checkbox').checked = isDyslexiaAidChecked;
    })

    // This closes the settings window - MW
    document.getElementById('btnExit').addEventListener('click', function () { CloseForm(); })

    document.addEventListener('DOMContentLoaded', function () {
      const table = document.getElementById('ResultsTable');
      let isResizing = false;
      let lastX = 0;
      let currentTh = null;

      table.querySelectorAll('th').forEach(th => {
        const div = document.createElement('div');
        div.classList.add('resize-handle');
        th.appendChild(div);
        div.addEventListener('mousedown', (e) => {
          isResizing = true;
          lastX = e.clientX;
          currentTh = th;
          document.body.style.cursor = 'col-resize';
        });
      });

      document.addEventListener('mousemove', (e) => {
        if (isResizing) {
          const dx = e.clientX - lastX;
          const newWidth = (currentTh.offsetWidth + dx) + 'px';
          currentTh.style.width = newWidth;
          lastX = e.clientX;
        }
      });

      document.addEventListener('mouseup', () => {
        if (isResizing) {
          isResizing = false;
          document.body.style.cursor = 'default';
        }
      });
    });

    function CloseForm() {
            window.close();
        }