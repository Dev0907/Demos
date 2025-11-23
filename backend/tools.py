"""
LangChain Tools for EduMind Agent
Provides math solving, plotting, table formatting, and document generation
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import sympy as sp
from sympy import symbols, solve, simplify, latex
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime

class MathSolver:
    """Solve mathematical equations and expressions"""
    
    @staticmethod
    def solve_equation(equation_str: str):
        """
        Solve an equation
        Example: "x**2 - 4 = 0" returns [2, -2]
        """
        try:
            x = symbols('x')
            equation = sp.sympify(equation_str)
            solutions = solve(equation, x)
            return {
                "solutions": [str(sol) for sol in solutions],
                "latex": latex(equation),
                "simplified": str(simplify(equation))
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def evaluate_expression(expr_str: str):
        """Evaluate a mathematical expression"""
        try:
            expr = sp.sympify(expr_str)
            result = expr.evalf()
            return {
                "result": str(result),
                "latex": latex(expr),
                "simplified": str(simplify(expr))
            }
        except Exception as e:
            return {"error": str(e)}

class PlotGenerator:
    """Generate plots and graphs"""
    
    @staticmethod
    def create_function_plot(function_str: str, x_range=(-10, 10), title="Function Plot"):
        """
        Create a plot of a mathematical function
        Returns base64 encoded image
        """
        try:
            x = symbols('x')
            expr = sp.sympify(function_str)
            f = sp.lambdify(x, expr, 'numpy')
            
            import numpy as np
            x_vals = np.linspace(x_range[0], x_range[1], 400)
            y_vals = f(x_vals)
            
            plt.figure(figsize=(8, 6))
            plt.plot(x_vals, y_vals, 'b-', linewidth=2)
            plt.grid(True, alpha=0.3)
            plt.xlabel('x', fontsize=12)
            plt.ylabel('f(x)', fontsize=12)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return {
                "image_base64": img_base64,
                "function": function_str,
                "latex": latex(expr)
            }
        except Exception as e:
            return {"error": str(e)}

class TableFormatter:
    """Format data into clean tables"""
    
    @staticmethod
    def create_table_data(headers: list, rows: list):
        """
        Create formatted table data
        """
        return {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
            "col_count": len(headers)
        }

class PDFExporter:
    """Export worksheets to PDF"""
    
    @staticmethod
    def create_worksheet_pdf(title: str, questions: list, answer_key: bool = True, output_path: str = None):
        """
        Create a professional worksheet PDF
        """
        if not output_path:
            output_path = f"static/generated/worksheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Instructions
        inst_style = ParagraphStyle(
            'Instructions',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20
        )
        story.append(Paragraph("Instructions: Answer all questions. Show your work for full credit.", inst_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Questions
        q_style = ParagraphStyle(
            'Question',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leftIndent=20
        )
        
        for i, q in enumerate(questions, 1):
            # Question number and text
            q_text = f"<b>Question {i}</b> ({q.get('difficulty', 'Medium')})<br/>{q['text']}"
            story.append(Paragraph(q_text, q_style))
            
            # Options for MCQ
            if q.get('options'):
                for opt in q['options']:
                    story.append(Paragraph(f"○ {opt}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            else:
                # Space for written answer
                story.append(Spacer(1, 0.5*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Answer Key (on new page)
        if answer_key:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            for i, q in enumerate(questions, 1):
                ans_text = f"<b>{i}.</b> {q.get('correct_answer', 'N/A')}"
                story.append(Paragraph(ans_text, styles['Normal']))
                
                if q.get('explanation'):
                    exp_text = f"<i>Explanation:</i> {q['explanation']}"
                    story.append(Paragraph(exp_text, inst_style))
                
                story.append(Spacer(1, 0.15*inch))
        
        doc.build(story)
        return output_path

class DiagramGenerator:
    """Generate flowcharts and diagrams"""
    
    @staticmethod
    def create_simple_flowchart(steps: list, title: str = "Flowchart"):
        """
        Create a simple vertical flowchart
        Returns base64 encoded image
        """
        try:
            fig, ax = plt.subplots(figsize=(8, len(steps) * 1.5))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, len(steps) * 2)
            ax.axis('off')
            
            # Title
            ax.text(5, len(steps) * 2 - 0.5, title, 
                   ha='center', va='top', fontsize=16, fontweight='bold')
            
            # Draw boxes and arrows
            for i, step in enumerate(steps):
                y_pos = len(steps) * 2 - (i + 1) * 2
                
                # Box
                box = plt.Rectangle((2, y_pos - 0.4), 6, 0.8, 
                                   facecolor='lightblue', edgecolor='black', linewidth=2)
                ax.add_patch(box)
                
                # Text
                ax.text(5, y_pos, step, ha='center', va='center', 
                       fontsize=11, wrap=True)
                
                # Arrow to next step
                if i < len(steps) - 1:
                    ax.arrow(5, y_pos - 0.5, 0, -0.9, 
                            head_width=0.3, head_length=0.2, fc='black', ec='black')
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return {
                "image_base64": img_base64,
                "steps": steps
            }
        except Exception as e:
            return {"error": str(e)}

# Tool instances
math_solver = MathSolver()
plot_generator = PlotGenerator()
table_formatter = TableFormatter()
pdf_exporter = PDFExporter()
diagram_generator = DiagramGenerator()
