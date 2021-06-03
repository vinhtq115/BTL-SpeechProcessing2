returnMessage = $('#returnMessage');
dataTable = $('#shiftTable');
idElement = $('#employeeID');

$('#checkButton').click(function(e) {
    e.preventDefault();

    $.get('/list_shift_api', {id: idElement.val()}, function(data, status) {
        console.log(data);

        if (data.status != 0) {
            returnMessage.children(0).text(data.message);
        } else {
            returnMessage.children(0).text("Employee: " + data.name);

            tableArr = data.data;
            dataTable.html('');
            for (i = 0; i < tableArr.length; i++) {
                 var row = document.createElement("tr");
                 var no = document.createElement("td");
                 no.innerText = tableArr[i].id;
                 row.appendChild(no);
                 var begin = document.createElement("td");
                 begin.innerText = tableArr[i].startDate;
                 row.appendChild(begin);
                 var end = document.createElement("td");
                 if (tableArr[i].endDate == null) {
                    row.classList = "table-success";
                    end.innerText = "Not finished yet";
                 } else {
                    end.innerText = tableArr[i].endDate;
                 }
                 row.appendChild(end);

                 dataTable.append(row);
            }
        }
        returnMessage.show();
    });
});

//