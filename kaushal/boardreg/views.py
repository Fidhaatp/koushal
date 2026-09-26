# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.urls import reverse
from .forms import BoardRegistrationForm
from .models import BoardRegistration, Faculty, CourseType, Course, Stream, Session, ModeOfStudy, Duration
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os
import json


APPRAISAL_DOC_RELATIVE = os.path.join(
    'boardreg', 'pdf', 'Placement_Assurance_Policy_and_Agreement.pdf'
)
APPRAISAL_DOC_FALLBACK = os.path.join(
    'boardreg', 'pdf', 'Placement_Assurance_Policy_and_Agreement.docx'
)


def _is_data_science_registration(registration):
    """True when the registration course is Data Science (appraisal form applies)."""
    return bool(getattr(registration, 'is_data_science', False))


def _appraisal_doc_path(prefer_pdf=True):
    """Resolve Placement Assurance PDF (preferred) or DOCX path from STATIC / BASE_DIR."""
    rels = [APPRAISAL_DOC_RELATIVE, APPRAISAL_DOC_FALLBACK] if prefer_pdf else [APPRAISAL_DOC_FALLBACK, APPRAISAL_DOC_RELATIVE]
    bases = []
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root:
        bases.append(static_root)
    bases.extend([
        os.path.join(settings.BASE_DIR, 'static'),
        os.path.join(settings.BASE_DIR, 'boardreg', 'static'),
    ])
    for base in bases:
        for rel in rels:
            path = os.path.join(base, rel)
            if path and os.path.isfile(path):
                return path
    return None

def boardreg(request):
    # Pre-populate sample data if needed (for demo) - run this only once or use management command
    if not Faculty.objects.exists():
        Faculty.objects.create(name='Arts')
        Faculty.objects.create(name='Science')
        Faculty.objects.create(name='Commerce')
        Faculty.objects.create(name='Engineering')

    # Create CourseTypes if none exist
    if not CourseType.objects.exists():
        CourseType.objects.create(name='Undergraduate')
        CourseType.objects.create(name='Postgraduate')
        CourseType.objects.create(name='Diploma')

# ==================== API ENDPOINTS FOR CASCADING DROPDOWNS ====================

# API: Get courses by course type
def get_courses_by_coursetype(request):
    course_type_id = request.GET.get('course_type_id')
    
    if not course_type_id:
        return JsonResponse([], safe=False)
    
    try:
        course_type_id = int(course_type_id)
        courses = Course.objects.filter(
            course_type_id=course_type_id
        ).values('id', 'name').order_by('name')
        
        return JsonResponse(list(courses), safe=False)
    
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)


# API: Get streams by course
def get_streams_by_course(request):
    course_id = request.GET.get('course_id')
    
    if not course_id:
        return JsonResponse([], safe=False)
    
    try:
        course_id = int(course_id)
        streams = Stream.objects.filter(
            course_id=course_id
        ).values('id', 'name').order_by('name')
        
        return JsonResponse(list(streams), safe=False)
    
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)


# API: Get sessions by course
def get_sessions_by_course(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse([], safe=False)
    try:
        course_id = int(course_id)
        sessions = Session.objects.filter(course_id=course_id).values('id', 'name').order_by('name')
        return JsonResponse(list(sessions), safe=False)
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)


# API: Get modes of study by course
def get_modes_by_course(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse([], safe=False)
    try:
        course_id = int(course_id)
        modes = ModeOfStudy.objects.filter(course_id=course_id).values('id', 'name').order_by('name')
        return JsonResponse(list(modes), safe=False)
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)


# API: Get durations by course
def get_durations_by_course(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse([], safe=False)
    try:
        course_id = int(course_id)
        durations = Duration.objects.filter(course_id=course_id).values('id', 'name').order_by('name')
        return JsonResponse(list(durations), safe=False)
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)


# API: Get faculty by course (returns single object)
def get_faculty_by_course(request):
    course_id = request.GET.get('course_id')
    
    if not course_id:
        return JsonResponse({'error': 'No course_id provided'}, status=400)
    
    try:
        course_id = int(course_id)
        course = Course.objects.select_related('faculty').get(id=course_id)
        
        if course.faculty:
            return JsonResponse({
                'id': course.faculty.id,
                'name': course.faculty.name
            })
        else:
            return JsonResponse({'id': None, 'name': 'No faculty assigned'})
    
    except (ValueError, TypeError, Course.DoesNotExist):
        return JsonResponse({'error': 'Course not found'}, status=404)

# ==================== REGISTRATION VIEW ====================

def boardreg_form(request):
    if request.method == 'POST':
        form = BoardRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save()
            messages.success(request, 'Registration submitted successfully!')

            # If this is an AJAX request, return JSON so frontend can show SweetAlert + PDF button
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                download_path = reverse('boardreg:download_pdf', args=[registration.id])
                download_url = request.build_absolute_uri(download_path)
                payload = {
                    'success': True,
                    'registration_id': registration.id,
                    'download_url': download_url,
                    'is_data_science': _is_data_science_registration(registration),
                    'appraisal_url': None,
                }
                if payload['is_data_science']:
                    appraisal_path = reverse('boardreg:download_appraisal', args=[registration.id])
                    payload['appraisal_url'] = request.build_absolute_uri(appraisal_path)
                return JsonResponse(payload)

            # Fallback: normal redirect to success page
            return redirect('boardreg:registration_success', registration_id=registration.id)
        else:
            # Validation errors (ensure JSON-serializable dict)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {k: list(v) for k, v in form.errors.items()}
                return JsonResponse(
                    {
                        'success': False,
                        'errors': errors_dict,
                    },
                    status=400,
                )
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BoardRegistrationForm()
    
    context = {
        "is_index": True,
        'form': form
    }
    return render(request, "boardreg/boardreg.html", context)


# Keep original name for URL pattern
boardreg = boardreg_form


def registration_success(request, registration_id):
    """Success page after registration with download option"""
    registration = get_object_or_404(BoardRegistration, id=registration_id)
    context = {
        'registration': registration,
        'is_data_science': _is_data_science_registration(registration),
    }
    return render(request, "boardreg/registration_success.html", context)


def dashboard(request):
    """Dashboard to view all registrations"""
    registrations = BoardRegistration.objects.all().order_by('-created_at')
    context = {
        'registrations': registrations,
    }
    return render(request, "boardreg/dashboard.html", context)


def download_appraisal_form(request, registration_id):
    """Download Placement Assurance Policy PDF — Data Science only.
    Overlays Student Name, Register No, Batch, Email, Internship ID, and Date onto the PDF template.
    """
    from datetime import date
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.pdfbase import pdfmetrics as rl_metrics

    def _title_case(value):
        """First letter of each word capital, rest small (e.g. thashmeer -> Thashmeer)."""
        text = (value or '').strip()
        if not text:
            return ''
        # Preserve separators like - / while title-casing word parts
        parts = []
        for chunk in text.replace('_', ' ').split():
            sub = []
            for piece in chunk.split('-'):
                sub.append(piece[:1].upper() + piece[1:].lower() if piece else '')
            parts.append('-'.join(sub))
        return ' '.join(parts)

    registration = get_object_or_404(BoardRegistration, id=registration_id)
    if not _is_data_science_registration(registration):
        raise Http404('Appraisal form is only available for Data Science registrations.')
    doc_path = _appraisal_doc_path(prefer_pdf=True)
    if not doc_path or not doc_path.lower().endswith('.pdf'):
        raise Http404('Appraisal form PDF not found.')

    student_name = _title_case(registration.candidate_name)
    register_no = (
        (getattr(registration, 'register_no', None) or '').strip() or str(registration.id)
    ).upper()
    internship_id = (
        (getattr(registration, 'internship_id', None) or '').strip() or register_no
    ).upper()
    email = (registration.email or '').strip().lower()
    batch = ''
    if registration.session and registration.session.name:
        batch = _title_case(registration.session.name)
    elif registration.month_session:
        year = registration.created_at.year if registration.created_at else ''
        batch = _title_case(f"{registration.month_session} {year}".strip())
    # Section 19 Date = download date; Section 20 Institute Date left blank for handwriting
    download_date = date.today().strftime('%d-%m-%Y')

    # Prefer Lexend if already registered for admission PDF; else Helvetica
    font_name = 'Helvetica'
    try:
        rl_metrics.getFont('Lexend')
        font_name = 'Lexend'
    except Exception:
        pass

    reader = PdfReader(doc_path)
    page_w = float(reader.pages[0].mediabox.width)
    page_h = float(reader.pages[0].mediabox.height)

    # Overlay canvas — match current template page size (A4: ~595 x 842)
    overlay_buf = BytesIO()
    c = pdf_canvas.Canvas(overlay_buf, pagesize=(page_w, page_h))
    c.setFillColorRGB(0, 0, 0)
    c.setFont(font_name, 11)

    # pdfminer y0 is slightly below ReportLab baseline; small lift keeps values on the label line
    y_fix = 3.0
    # Agreement Parties value column (same x as NATDEMY / Program)
    parties_value_x = 216.1

    # --- Page 1 (index 0): AGREEMENT PARTIES ---
    c.drawString(parties_value_x, 443.8 + y_fix, student_name[:60])
    c.drawString(parties_value_x, 416.0 + y_fix, register_no[:40])
    c.drawString(parties_value_x, 388.4 + y_fix, batch[:40])
    c.showPage()

    # Blank overlays for middle pages (1..6) — template has 8 pages total
    middle_count = max(0, len(reader.pages) - 2)
    for _ in range(middle_count):
        c.showPage()

    # --- Last page: Section 19 student fields + Section 20 institute date ---
    # Layout: Student Name | Register No
    #         Student Signature | Email Address
    #         Date | Internship ID
    c.setFont(font_name, 11)
    c.drawString(168.0, 527.8 + y_fix, student_name[:40])          # after Student Name:
    c.drawString(402.0, 527.8 + y_fix, register_no[:28])           # after Register No:
    # Student Signature left blank
    c.drawString(420.0, 493.3 + y_fix, email[:32])                 # after Email Address:
    c.drawString(120.0, 458.4 + y_fix, download_date)              # Date (download date)
    c.drawString(412.0, 458.4 + y_fix, internship_id[:28])         # after Internship ID:
    # Section 20 Institute Date left blank (handwritten); Name/Designation already in template
    c.showPage()
    c.save()
    overlay_buf.seek(0)

    overlay_reader = PdfReader(overlay_buf)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i < len(overlay_reader.pages):
            page.merge_page(overlay_reader.pages[i])
        writer.add_page(page)

    out = BytesIO()
    writer.write(out)
    out.seek(0)

    safe_name = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in student_name) or 'student'
    filename = f"Placement_Assurance_{safe_name}_{register_no}.pdf"
    response = HttpResponse(out.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# University branding for PDF (customize as needed)
PDF_UNIVERSITY_NAME = "Koushal Vikas University"
PDF_UNIVERSITY_SUBTITLE = "Established under section 2(f) of UGC act, 1956"
PDF_PHONE = "+91 9899108107"
PDF_WEBSITE = "www.kvss.co.in"
PDF_EMAIL = "info@kvss.co.in"

# Declaration text for admission form PDF
PDF_DECLARATION = """I hereby declare that entries made by me in this admission form and the documents submitted by me along with it, are true to the best of my knowledge, in all respects and in any case, if any information is found to be false, this shall entail automatic cancellation of my admission and forfeiture of all fee deposited, besides rendering me liable to such action as the University may deem proper.

I take note that my admission to the University and continuation on its roll are subject to the provisions of rules of the University, issued from time to time. I shall abide by the rules of discipline and proper conduct. I am fully aware of the law regarding ragging as well as the punishment and that if, found guilty on this account I am liable to be punished appropriately. I hereby undertake that I shall not indulge in any act of ragging.

In such circumstances, I will have no claim for refund of fees deposited by me to the University."""


def download_registration_pdf(request, registration_id):
    """Generate and download PDF in university admission form style (Asian International University style)."""
    registration = get_object_or_404(BoardRegistration, id=registration_id)

    response = HttpResponse(content_type='application/pdf')
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in registration.candidate_name)
    # response['Content-Disposition'] = f'attachment; filename="ADMISSION FORM OF {safe_name}.pdf"'
    response['Content-Disposition'] = f'attachment; filename="ADMISSION FORM OF {safe_name.upper()}.pdf"'
 
    # response['Content-Disposition'] = f'attachment; filename="admission_form_{registration.id}_{safe_name}.pdf"'

    # Theme color; reduced side margins for full-width content
    theme_blue = colors.HexColor('#002147')
    margin_pt = 36  # 0.5" left/right for less padding, wider content
    content_width = (595 - 2 * margin_pt) / 72.0  # A4 width in inch

    # Register Lexend font if TTF files exist (download from Google Fonts if needed)
    pdf_font = 'Helvetica'
    pdf_font_bold = 'Helvetica-Bold'
    for base in [settings.BASE_DIR, os.path.join(settings.BASE_DIR, '..')]:
        for font_dir in ['static/boardreg/fonts', 'static/fonts', 'boardreg/static/fonts']:
            d = os.path.join(base, font_dir) if isinstance(base, str) else os.path.join(base, *font_dir.split('/'))
            reg_path = os.path.join(d, 'Lexend-Regular.ttf')
            bold_path = os.path.join(d, 'Lexend-Bold.ttf')
            if os.path.isfile(reg_path) and os.path.isfile(bold_path):
                try:
                    pdfmetrics.registerFont(TTFont('Lexend', reg_path))
                    pdfmetrics.registerFont(TTFont('Lexend-Bold', bold_path))
                    pdf_font = 'Lexend'
                    pdf_font_bold = 'Lexend-Bold'
                except Exception:
                    pass
                break
        if pdf_font == 'Lexend':
            break

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=margin_pt, rightMargin=margin_pt,
        topMargin=42, bottomMargin=42,
    )
    elements = []
    styles = getSampleStyleSheet()
    dark_text = colors.HexColor('#1e293b')
    grey_border = colors.HexColor('#64748b')
    grey_light = colors.HexColor('#f1f5f9')

    def _txt(s):
        if s is None or (isinstance(s, str) and not s.strip()):
            return "—"
        return str(s).strip()

    def _txt_cap(s):
        """Same as _txt but uppercase; use for all table data except email."""
        return _txt(s).upper()

    def _fee(v):
        """Fee string without rupee symbol (avoids square in PDF)."""
        if v is None:
            return "—"
        return "Rs. {:,.2f}".format(float(v))

    def _section_header(title):
        t = Table([[title]], colWidths=[content_width*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), theme_blue),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), pdf_font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ]))
        return t

    # ---- Header: official style — logo left, text block right, all left-aligned ----
    def _image_with_ratio(path, max_width_inch, max_height_inch):
        """Load image and set draw size preserving aspect ratio (no stretch)."""
        try:
            ir = ImageReader(path)
            iw, ih = ir.getSize()
            if iw <= 0 or ih <= 0:
                return None
            scale = min(max_width_inch * 72 / iw, max_height_inch * 72 / ih, 1.0)
            img = Image(path)
            img.drawWidth = iw * scale
            img.drawHeight = ih * scale
            return img
        except Exception:
            return None

    class RoundedLogoBox(Flowable):
        def __init__(self, image_path=None, box_width=1.45 * inch, box_height=1.45 * inch, radius=10):
            super().__init__()
            self.image_path = image_path
            self.box_width = box_width
            self.box_height = box_height
            self.radius = radius
            self.width = box_width
            self.height = box_height

        def wrap(self, availWidth, availHeight):
            return self.box_width, self.box_height

        def draw(self):
            c = self.canv
            c.saveState()
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.white)
            c.roundRect(0, 0, self.box_width, self.box_height, self.radius, stroke=0, fill=1)

            if self.image_path and os.path.isfile(self.image_path):
                try:
                    ir = ImageReader(self.image_path)
                    iw, ih = ir.getSize()
                    if iw > 0 and ih > 0:
                        pad = 10
                        max_w = self.box_width - (pad * 2)
                        max_h = self.box_height - (pad * 2)
                        scale = min(max_w / iw, max_h / ih, 1.0)
                        draw_w = iw * scale
                        draw_h = ih * scale
                        x = (self.box_width - draw_w) / 2.0
                        y = (self.box_height - draw_h) / 2.0
                        c.drawImage(ir, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
                except Exception:
                    pass
            c.restoreState()

    logo_cell = ''
    logo_path = None
    for base in [settings.STATIC_ROOT, settings.BASE_DIR, os.path.join(settings.BASE_DIR, '..')]:
        if not base:
            continue
        for sub in ['web/static/web/images/unv/logo.png', 'web/images/unv/logo.png', 'static/web/images/unv/logo.png']:
            p = os.path.join(base, *sub.split('/')) if isinstance(base, str) else os.path.join(base, sub)
            if os.path.isfile(p):
                logo_img = _image_with_ratio(p, 1.45, 1.35)
                if logo_img:
                    logo_cell = logo_img
                    logo_path = p
                break
        if logo_cell:
            break

    header_bg = colors.HexColor('#002147')
    header_text = colors.white
    logo_box_w = 1.7 * inch
    text_col_w = (content_width * inch) - logo_box_w

    # Header banner text
    univ_style = ParagraphStyle(
        'UnivName', parent=styles['Normal'], fontSize=14, textColor=header_text,
        alignment=TA_LEFT, fontName=pdf_font_bold, leftIndent=0,
        leading=16, spaceBefore=0, spaceAfter=0
    )
    sub_style = ParagraphStyle(
        'UnivSub', parent=styles['Normal'], fontName=pdf_font,
        fontSize=8, textColor=header_text, alignment=TA_LEFT,
        leftIndent=0, leading=12, spaceBefore=0, spaceAfter=0
    )
    contact_style = ParagraphStyle(
        'Contact', parent=styles['Normal'], fontName=pdf_font,
        fontSize=8, textColor=header_text,
        alignment=TA_LEFT, leftIndent=0, leading=12, spaceBefore=0, spaceAfter=0
    )
    text_block = [
        Paragraph(PDF_UNIVERSITY_NAME.upper(), univ_style),
        Paragraph(PDF_UNIVERSITY_SUBTITLE, sub_style),
        Paragraph('Website: {} | Email: {}'.format(
            PDF_WEBSITE, PDF_EMAIL), contact_style),
    ]

    inner_table = Table(
        [[text_block[0]], [text_block[1]], [text_block[2]]],
        colWidths=[text_col_w]
    )
    inner_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 3),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 1), (-1, 2), 3),
        ('BOTTOMPADDING', (0, 1), (-1, 2), 3),
    ]))

    logo_card = RoundedLogoBox(logo_path, box_width=1.14 * inch, box_height=1.14 * inch, radius=10)
    logo_table = Table([[logo_card]], colWidths=[1.14 * inch], rowHeights=[1.14 * inch])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    header_table = Table([[logo_table, inner_table]], colWidths=[logo_box_w, text_col_w], rowHeights=[1.32 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), header_bg),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ('LEFTPADDING', (1, 0), (1, -1), 12),
        ('RIGHTPADDING', (1, 0), (1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    # ADMISSION FORM — same style as section headings (blue bar, white text)
    elements.append(_section_header('ADMISSION FORM'))
    elements.append(Spacer(1, 12))

    # Admission summary: Name / Course on left, Register No / Internship ID on right, plus Photo block
    course_display = registration.course.name if registration.course else "—"
    stream_display = registration.stream.name if registration.stream else "—"
    name_display = _txt(registration.candidate_name).upper()
    register_display = _txt(getattr(registration, "register_no", None)) or "—"
    internship_display = _txt(getattr(registration, "internship_id", None)) or "—"

    # Use Paragraphs so long values (e.g. course name) wrap instead of overlapping the next column
    hdr_val_style = ParagraphStyle(
        'HdrVal', parent=styles['Normal'], fontName=pdf_font, fontSize=8,
        leading=10, textColor=dark_text, alignment=TA_LEFT,
    )
    hdr_lbl_style = ParagraphStyle(
        'HdrLbl', parent=styles['Normal'], fontName=pdf_font_bold, fontSize=8,
        leading=10, textColor=dark_text, alignment=TA_LEFT,
    )

    # Wider value column for course/name; slightly narrower for register/internship
    left_w = (content_width - 1.4) * inch
    header_label_w = 1.25 * inch
    header_label2_w = 1.15 * inch
    header_value_w = (left_w - header_label_w - header_label2_w) * 0.58
    header_value2_w = left_w - header_label_w - header_label2_w - header_value_w

    left_data = [
        [
            Paragraph('CANDIDATE NAME', hdr_lbl_style),
            Paragraph(_txt(name_display), hdr_val_style),
            Paragraph('REGISTER NO', hdr_lbl_style),
            Paragraph(_txt(register_display), hdr_val_style),
        ],
        [
            Paragraph('COURSE NAME', hdr_lbl_style),
            Paragraph(_txt(course_display).upper() if course_display != '—' else '—', hdr_val_style),
            Paragraph('INTERNSHIP ID', hdr_lbl_style),
            Paragraph(_txt(internship_display), hdr_val_style),
        ],
    ]
    left_table = Table(
        left_data,
        colWidths=[header_label_w, header_value_w, header_label2_w, header_value2_w],
    )
    left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (0, -1), 2),
        ('RIGHTPADDING', (0, 0), (0, -1), 6),
        ('LEFTPADDING', (1, 0), (1, -1), 4),
        ('RIGHTPADDING', (1, 0), (1, -1), 10),
        ('LEFTPADDING', (2, 0), (2, -1), 8),
        ('RIGHTPADDING', (2, 0), (2, -1), 6),
        ('LEFTPADDING', (3, 0), (3, -1), 4),
        ('RIGHTPADDING', (3, 0), (3, -1), 2),
    ]))
    photo_cell = ''
    try:
        if registration.photo and hasattr(registration.photo, 'path') and os.path.exists(registration.photo.path):
            photo_img = _image_with_ratio(registration.photo.path, 1.15, 1.25)
            if photo_img:
                photo_cell = photo_img
    except Exception:
        pass
    top_table = Table([[left_table, photo_cell]], colWidths=[left_w, 1.4 * inch])
    top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(top_table)
    elements.append(Spacer(1, 16))

    # ---- GENERAL INFORMATION: two tables side-by-side (col-6 / col-6) ----
    elements.append(_section_header('GENERAL INFORMATION'))
    elements.append(Spacer(1, 8))

    gender_display = getattr(registration, 'get_gender_display', lambda: registration.gender)()
    category_display = getattr(registration, 'get_category_display', lambda: registration.category)()
    country_display = _txt(getattr(registration, 'country', None)) or (getattr(registration, 'get_country_display', lambda: None)() or '—')
    mode_display = _txt(registration.mode_of_study.name if registration.mode_of_study else None) or 'Regular'
    # Course fee: use registration's saved fee, else fall back to course's application_fee (for server/legacy data)
    fee_value = registration.application_fee
    if fee_value is None and getattr(registration, 'course', None):
        fee_value = getattr(registration.course, 'application_fee', None)
    course_fee_str = _fee(fee_value)
    # Build address from address information fields
    addr_parts = [
        _txt(getattr(registration, 'House_Building_Name_or_Number', None)),
        _txt(getattr(registration, 'Street_Name', None)),
        _txt(getattr(registration, 'post_office_name', None)),
        _txt(getattr(registration, 'village_town_city', None)),
        _txt(getattr(registration, 'district', None)),
        _txt(getattr(registration, 'State', None)),
        _txt(getattr(registration, 'pincode', None)),
    ]
    address_str = ', '.join(p for p in addr_parts if p).strip() or '—'
    address_para = Paragraph(address_str.replace('\n', '<br/>'), ParagraphStyle('Addr', parent=styles['Normal'], fontName=pdf_font, fontSize=8, leading=10))

    # Column widths: left pair, a small gap, then right pair
    gap_w = 0.15 * inch
    gen_label_w = 1.3 * inch
    gen_value_w = ((content_width - 0.15) / 2.0 - 1.3) * inch

    def _gen_table_style():
        return TableStyle([
            ('FONTNAME', (0, 0), (0, -1), pdf_font_bold),
            ('FONTNAME', (3, 0), (3, -1), pdf_font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            # More gap between field label and data value (left and right columns)
            ('RIGHTPADDING', (0, 0), (0, -1), 36),
            ('LEFTPADDING', (1, 0), (1, -1), 24),
            ('RIGHTPADDING', (3, 0), (3, -1), 36),
            ('LEFTPADDING', (4, 0), (4, -1), 24),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, grey_border),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, grey_border),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, grey_border),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, grey_border),
            ('LINEBELOW', (0, 3), (-1, 3), 0.5, grey_border),
            ('LINEBELOW', (0, 4), (-1, 4), 0.5, grey_border),
            ('LINEBELOW', (0, 5), (-1, 5), 0.5, grey_border),
            ('LINEBELOW', (0, 6), (-1, 6), 0.5, grey_border),
        ])

    # GENERAL INFORMATION: all data in CAPITAL except Mail (email kept as-is)
    hostel_display = 'Yes' if getattr(registration, 'hostel_facility', None) == 'yes' else 'No'
    gen_rows = [
        ['NAME OF CANDIDATE', ' ' + _txt_cap(registration.candidate_name), '', 'CONTACT NO', _txt_cap(registration.contact_number)],
        ['DATE OF BIRTH', ' ' + (registration.date_of_birth.strftime('%d-%m-%Y') if registration.date_of_birth else '—'), '', 'MAIL', _txt(registration.email)],
        ['GENDER', ' ' + _txt_cap(gender_display), '', 'CATEGORY', _txt_cap(category_display)],
        ["FATHER'S NAME", ' ' + _txt_cap(registration.father_name), '', 'CONTACT NO', _txt_cap(registration.father_contact)],
        ["MOTHER'S NAME", ' ' + _txt_cap(registration.mother_name), '', 'CONTACT NO', _txt_cap(registration.mother_contact)],
        ['ID PROOF TYPE', ' ' + _txt_cap(registration.id_proof_type), '', 'ID PROOF NO', _txt_cap(registration.id_proof_no)],
        ['CURRENTLY EMPLOYED?', ' ' + _txt_cap(registration.employed), '', 'HOSTEL', _txt_cap(hostel_display)],
    ]
    gen_table = Table(gen_rows, colWidths=[gen_label_w, gen_value_w, gap_w, gen_label_w, gen_value_w])
    gen_table.setStyle(_gen_table_style())
    elements.append(gen_table)
    elements.append(Spacer(1, 14))

    # ---- ADDRESS INFORMATION ----
    elements.append(_section_header('ADDRESS INFORMATION'))
    elements.append(Spacer(1, 8))

    addr_rows = [
        ['COUNTRY', ' ' + (_txt_cap(getattr(registration, 'country', None)) or '—'), '', 'NATIONALITY', ' ' + (_txt_cap(getattr(registration, 'nationality', None)) or '—')],
        ['HOUSE NAME', ' ' + (_txt_cap(getattr(registration, 'House_Building_Name_or_Number', None)) or '—'), '', '', ''],
        ['STREET NAME', ' ' + (_txt_cap(getattr(registration, 'Street_Name', None)) or '—'), '', 'TOWN', ' ' + (_txt_cap(getattr(registration, 'village_town_city', None)) or '—')],
        ['DISTRICT', ' ' + (_txt_cap(getattr(registration, 'district', None)) or '—'), '', 'STATE', ' ' + (_txt_cap(getattr(registration, 'State', None)) or '—')],
        ['POST OFFICE', ' ' + (_txt_cap(getattr(registration, 'post_office_name', None)) or '—'), '', 'PINCODE', ' ' + (_txt_cap(getattr(registration, 'pincode', None)) or '—')],
    ]
    addr_table = Table(addr_rows, colWidths=[gen_label_w, gen_value_w, gap_w, gen_label_w, gen_value_w])
    addr_table.setStyle(_gen_table_style())
    elements.append(addr_table)
    elements.append(Spacer(1, 14))

    # ---- PROGRAMME DETAILS ----
    elements.append(_section_header('PROGRAMME DETAILS'))
    elements.append(Spacer(1, 8))

    duration_display = registration.duration.name if registration.duration else "—"
    session_name = registration.session.name if registration.session else "—"
    mode_name = registration.mode_of_study.name if registration.mode_of_study else "—"

    # PROGRAMME DETAILS in two halves, row-style like GENERAL INFORMATION
    # Reuse GENERAL INFORMATION widths so alignment matches
    prog_label_w = gen_label_w
    prog_value_w = gen_value_w

    def _prog_table_style():
        return TableStyle([
            ('FONTNAME', (0, 0), (0, -1), pdf_font_bold),
            ('FONTNAME', (3, 0), (3, -1), pdf_font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (0, -1), 36),
            ('LEFTPADDING', (1, 0), (1, -1), 24),
            ('RIGHTPADDING', (3, 0), (3, -1), 36),
            ('LEFTPADDING', (4, 0), (4, -1), 24),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, grey_border),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, grey_border),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, grey_border),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, grey_border),
            ('LINEBELOW', (0, 3), (-1, 3), 0.5, grey_border),
            ('LINEBELOW', (0, 4), (-1, 4), 0.5, grey_border),
            ('LINEBELOW', (0, 5), (-1, 5), 0.5, grey_border),
        ])

    date_of_join_str = registration.date_of_join.strftime('%d-%m-%Y') if getattr(registration, 'date_of_join', None) else '—'
    academic_delivery_end_str = registration.academic_delivery_end.strftime('%d-%m-%Y') if getattr(registration, 'academic_delivery_end', None) else '—'
    branch_display = _txt(registration.branch.name if getattr(registration, 'branch', None) else None) or '—'
    month_session_display = registration.get_month_session_display() if getattr(registration, 'month_session', None) else '—'

    # Single 5-column table: all data in CAPITAL
    prog_rows = [
        ['DATE OF JOIN', ' ' + date_of_join_str, '', 'DURATION', _txt_cap(duration_display)],
        ['COURSE TYPE', ' ' + _txt_cap(registration.course_type.name if registration.course_type else None), '', 'MODE OF STUDY', _txt_cap(mode_name)],
        ['COURSE', ' ' + _txt_cap(course_display), '', 'STREAM', ' ' + _txt_cap(stream_display)],
        ['MONTHLY SESSION', ' ' + _txt_cap(month_session_display), '', 'SESSION', ' ' + _txt_cap(session_name)],
        ['BRANCH', ' ' + _txt_cap(branch_display), '', 'ACADEMIC END', academic_delivery_end_str],
        ['COURSE FEE', ' ' + _txt_cap(course_fee_str), '', '', ''],
    ]
    prog_table = Table(prog_rows, colWidths=[prog_label_w, prog_value_w, gap_w, prog_label_w, prog_value_w])
    prog_table.setStyle(_prog_table_style())
    elements.append(prog_table)
    elements.append(Spacer(1, 14))

    # ---- QUALIFICATION INFORMATION ----
    elements.append(_section_header('QUALIFICATION INFORMATION'))
    elements.append(Spacer(1, 8))

    # Paragraph style for qualification cells so long text wraps (fixes overlap in Examination & Board/University)
    qual_para_style = ParagraphStyle(
        'QualCell', parent=styles['Normal'], fontName=pdf_font, fontSize=8,
        leading=10, leftIndent=0, rightIndent=0, spaceBefore=0, spaceAfter=0,
    )
    qual_para_style_bold = ParagraphStyle(
        'QualCellBold', parent=qual_para_style, fontName=pdf_font_bold
    )

    def _qual_para(text, bold=False, upper=False):
        if not text and text != 0:
            return Paragraph("—", qual_para_style)
        s = _txt(text)
        if not s or s == "—":
            return Paragraph("—", qual_para_style)
        if upper:
            s = s.upper()
        s_esc = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return Paragraph(s_esc, qual_para_style_bold if bold else qual_para_style)

    def _board_para(text, upper=False):
        """Board/University column: wrap long names with <br/> for readability."""
        if not text or not str(text).strip():
            return Paragraph("—", qual_para_style)
        s = _txt(text)
        if upper:
            s = s.upper()
        s_esc = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if len(s) > 42:
            for phrase in [' GOVERNMENT ', ' STATE ', ' EXAMINATIONS ']:
                if phrase in s_esc:
                    s_esc = s_esc.replace(phrase, '<br/>' + phrase.strip() + ' ', 1)
                    break
        return Paragraph(s_esc, qual_para_style)

    qual_data = [[
        _qual_para('EXAMINATION', bold=True),
        _qual_para('YEAR', bold=True),
        _qual_para('BOARD / UNIVERSITY', bold=True),
        _qual_para('MARKS (%)', bold=True),
    ]]
    qual_data.append([
        _qual_para('SECONDARY (CLASS X)'),
        _qual_para(registration.secondary_year, upper=True),
        _board_para(registration.secondary_board, upper=True),
        _qual_para(registration.secondary_percentage, upper=True),
    ])
    if registration.srsecondary_board:
        qual_data.append([
            _qual_para('SENIOR SECONDARY (CLASS XII)'),
            _qual_para(registration.srsecondary_year, upper=True),
            _board_para(registration.srsecondary_board, upper=True),
            _qual_para(registration.srsecondary_percentage, upper=True),
        ])
    if registration.graduation_board:
        qual_data.append([
            _qual_para('GRADUATION'),
            _qual_para(registration.graduation_year, upper=True),
            _board_para(registration.graduation_board, upper=True),
            _qual_para(registration.graduation_percentage, upper=True),
        ])
    if registration.postgraduation_board:
        qual_data.append([
            _qual_para('POST GRADUATION'),
            _qual_para(registration.postgraduation_year, upper=True),
            _board_para(registration.postgraduation_board, upper=True),
            _qual_para(registration.postgraduation_percentage, upper=True),
        ])
    if registration.other_board:
        qual_data.append([
            _qual_para('OTHER'),
            _qual_para(registration.other_year, upper=True),
            _board_para(registration.other_board, upper=True),
            _qual_para(registration.other_percentage, upper=True),
        ])
    # Wider Examination column to prevent overlap; Board/University gets remaining width for wrapping
    qual_cols = [1.85*inch, 0.7*inch, (content_width - 3.6)*inch, 1.05*inch]
    qual_table = Table(qual_data, colWidths=qual_cols)
    qual_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), pdf_font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, grey_border),
        ('BACKGROUND', (0, 0), (-1, 0), grey_light),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    elements.append(qual_table)
    elements.append(Spacer(1, 18))

    # ---- DECLARATION ----
    decl_left = 18
    decl_right = 18
    decl_inner_width = content_width * inch - decl_left - decl_right
    decl_title_style = ParagraphStyle(
        'DeclTitle', parent=styles['Normal'], fontSize=9, fontName=pdf_font_bold,
        alignment=TA_CENTER, spaceAfter=12, textColor=theme_blue
    )
    elements.append(Paragraph('DECLARATION', decl_title_style))
    decl_body_style = ParagraphStyle(
        'DeclBody', parent=styles['Normal'], fontSize=8, fontName=pdf_font,
        alignment=TA_JUSTIFY, leading=12, spaceAfter=0
    )
    decl_body_table = Table(
        [[Paragraph(PDF_DECLARATION.replace('\n', '<br/>'), decl_body_style)]],
        colWidths=[content_width * inch]
    )
    decl_body_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), decl_left),
        ('RIGHTPADDING', (0, 0), (-1, -1), decl_right),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(decl_body_table)

    sig_style = ParagraphStyle('Sig', parent=styles['Normal'], fontSize=8, fontName=pdf_font)
    label_style = ParagraphStyle('SigLabel', parent=sig_style)
    group_gap_w = 0.38 * inch
    name_label_w = 0.95 * inch
    sig_label_w = 0.72 * inch
    date_label_w = 0.42 * inch
    name_line_w = 1.80 * inch
    sig_line_w = 1.20 * inch
    date_line_w = decl_inner_width - (
        name_label_w + name_line_w + group_gap_w +
        sig_label_w + sig_line_w + group_gap_w +
        date_label_w
    )
    identity_table = Table(
        [[
            Paragraph('Student Name :', label_style), '',
            '',
            Paragraph('Signature :', label_style), '',
            '',
            Paragraph('Date :',label_style), '',
        ]],
        colWidths=[
            name_label_w, name_line_w, group_gap_w,
            sig_label_w, sig_line_w, group_gap_w,
            date_label_w, date_line_w,
        ]
    )
    identity_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 4),
        ('RIGHTPADDING', (3, 0), (3, 0), 4),
        ('RIGHTPADDING', (6, 0), (6, 0), 4),
        ('LINEBELOW', (1, 0), (1, 0), 0.6, colors.black),
        ('LINEBELOW', (4, 0), (4, 0), 0.6, colors.black),
        ('LINEBELOW', (7, 0), (7, 0), 0.6, colors.black),
    ]))
    identity_wrap = Table([[identity_table]], colWidths=[content_width * inch])
    identity_wrap.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), decl_left),
        ('RIGHTPADDING', (0, 0), (-1, -1), decl_right),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(identity_wrap)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def api_test(request):
    """Test page for API endpoints"""
    return render(request, "boardreg/api_test.html")