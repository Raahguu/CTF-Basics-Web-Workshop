<?php
$data = <<<HTML
<h3>How To</h3>
<p>Brainf*ck is a very simplistic language.<br>
    It operates on the principle that you have an infinite array of sequential registers, and each one can store an 8-bit unsigned integer (0-255); Each of these registers starts at '0'.<br>
    You also have a data pointer which points to a single register at a time and you can move around (starts at the 0th register).<br>
    And an instruction pointer which points to the current instruction to be ran (starts at the 0th charcater of the code), this increments by one by default with every instruction ran (think of it as the program counter).<br>
    The entire language is comprised of eight characacters that you can use to move the pointer and modify the values in the registers:<br>
</p>
<table>
    <tr>
        <th>Symbol</th>
        <th>Meaning</th>
    </tr>
    <tr>
        <td style="text-align:center"><code>></code></td>
        <td>Increment the data pointer by one (now points at the next register on the right)</td>
    </tr>
    <tr>
        <td style="text-align:center"><code><</code></td>
        <td>Deincrement the data pointer by one (now points at the next register on the left). Undefined if it is already at 0</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>+</code></td>
        <td>Increment the pointed at register by one modulo 256 (if the register goes over 255 it integer overflows back to 0)</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>-</code></td>
        <td>Deincrement the pointed at register by one modulo 256 (if the register goes under 0 it integer underflows back to 255)</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>.</code></td>
        <td>Outputs the byte in the pointed at register, normally as if the value was an ASCII code (or one of the Extended ASCII formats depending on implementation)</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>,</code></td>
        <td>Accepts one byte of user input storing it into the pointed at register (overwrites the value in the register) (typically converts any character provided to its ASCII value (implementation specific))</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>[</code></td>
        <td>If the pointed at register contains a zero, jumps the instruction pointer forward to its matching ']'</td>
    </tr>
    <tr>
        <td style="text-align:center"><code>]</code></td>
        <td>If the pointed at register is not zero, it jumps the instruction pointer back to its matching '['</td>
    </tr>
</table>

<p> As there are only 8 characters that are part of brainfuck, and it is turing complete and so has no need for anything else. All other charcaters are treated as comments</p>

<h4>Example - Hello World</h4>
<pre><code>
[       Becuase this loop is the first thing in the program, and all the registers start at '0',
        you can have an inital comment and can use any brainf*ck characters you want .<>+-
        without them doing anything as the entire loop is always skipped
        (this is of course only if the amount of '[' and ']' characters within the inital comment are equal)
]

++++++++            Set register 0 to '8'
[                   Start a loop
    >+++++++++      Add '9' to register 1
    <-              This would be an infite loop if we did not deincremnt register 0 in some way
]                   Ending character for the loop

>.                  Move to register 1 and print it
                    As register 1 is 72 (8*9) this prints 'H'

>                   Move to register 2
+++[>+++<-]         Increment it to '3' and then make a loop to increment register 3 to '9' while also deincrementing register 2 down to '0'
>+                  Register 3 is now '10'
[>+>+<<-]           Copy the value in register 3 into registers 4 and 5 while deincrementing 3 to '0'
>>[                 Go to register 6 and start a loop
    -<              Deincrement it by 1 and go to register 5
    [               Nested for loop
        -<+<+>>     Increment the value in register 2 and 3 to be the same as in register 4
    ]
    <               Move to register 3
    [->+<]          Copy the value in register 3 into register 4
    >>              Go from register 3 to register 5
]
<<<                 Go to register 2
+.                  Increment register 2 and print it which is 101 so 'e'

+++++++             Increment register 2 '7' times into '108'
..                  print 108 which is 'l' twice

+++.                Increment register 2 '3' times into '111' then print it out as 'o'

>>------            Move to register 4 and deincrement it from '10' to '4'
[<++++++++>-]<.     Make a loop incrementing register 3 by '8' everytime before printing it as '32' or ' '

<<<                 Move to register 0
+++++[>+++<-]>.     Set it to '5' and make a loop incrementing register 1 by '3' into '87' (72 add 15) before printing it as 'W'

>.                  Move to register 2 which is '111' and print it as 'o'
+++.                Increment it by '3' to '114' and print it as 'r'
------.             Deincrement by '6' to '108' and print it as 'l'
<<++++[>>--<<-]     Move to register 0 and set it to '4' then make a loop that deincrements register 2 by '2' everytime
                    Register 2 is now '100'
>>.                 Print register 2 as 'd'
>+.                 Move to register 3 which is '32' increment it to '33' and then print it as '!'
</code></pre>
HTML;
?>
