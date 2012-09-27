"""Provide filters and gadgets for jinja2 formatting of messages"""

from string import Template


def urlformat(uu, text=''):
    "create a nice HTML anchor"
    return '<a class="matrix-anchor" href="%s">%s</a>' % (uu, text or uu)

button = Template("""
<table align="center" border="0" cellpadding="0" cellspacing="0" width="360">
<tbody>
<tr>
<td>
<p style="width: 300px;
background: ${bcolour};
font-family: ${font};
font-size: 18px;
line-height: 18px; text-align:
center;margin: 10px auto 20px
auto;padding: 14px 10px;
-moz-border-radius: 6px;
-webkit-border-radius: 6px;
border-radius: 6px;">
<a moz-do-not-send="true" href="${uu}"
 style="color: ${fcolour}; text-decoration: none;">
 <strong>${text}</strong>
</a></p>
</td>
</tr>
</tbody>
</table>
""")


def buttonformat(uu,
  text='',
  bcolour='#29ABE2',
  fcolour='#fff',
  font='arial, sans-serif'):
    "Makes a nice phat button in the middle of the page"
    return button.substitute(uu=uu,
        text=text,
        bcolour=bcolour,
        fcolour=fcolour,
        font=font)
