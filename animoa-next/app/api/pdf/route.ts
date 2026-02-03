import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { jsPDF } from 'jspdf'
import type { AssessmentResponses } from '@/types'

const responseLabels: Record<string, Record<string, string>> = {
  mood: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  interest: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  anxiety: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  worry: {
    not_at_all: 'Not at all',
    several_days: 'Several days',
    more_than_half: 'More than half the days',
    nearly_every_day: 'Nearly every day',
  },
  sleep: {
    very_good: 'Very good',
    good: 'Good',
    fair: 'Fair',
    poor: 'Poor',
    very_poor: 'Very poor',
  },
  support: {
    strong: 'Strong support network',
    moderate: 'Moderate support',
    limited: 'Limited support',
    none: 'Little to no support',
  },
}

const frequencyScore: Record<string, number> = {
  not_at_all: 0,
  several_days: 1,
  more_than_half: 2,
  nearly_every_day: 3,
}

// POST /api/pdf - Generate a wellness report PDF for an assessment
export async function POST(request: NextRequest) {
  try {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { assessmentId } = await request.json() as { assessmentId: string }

    if (!assessmentId) {
      return NextResponse.json({ error: 'Assessment ID is required' }, { status: 400 })
    }

    // Fetch assessment
    const { data: assessment, error } = await supabase
      .from('questionnaire_responses')
      .select('*')
      .eq('id', assessmentId)
      .eq('user_id', user.id)
      .single()

    if (error || !assessment) {
      return NextResponse.json({ error: 'Assessment not found' }, { status: 404 })
    }

    // Fetch user profile
    const { data: profile } = await supabase
      .from('profiles')
      .select('full_name, email')
      .eq('id', user.id)
      .single()

    const responses = assessment.responses as AssessmentResponses
    const recommendations = assessment.recommendations as string | null

    // Calculate scores
    const phq2 = (frequencyScore[responses.mood] || 0) + (frequencyScore[responses.interest] || 0)
    const gad2 = (frequencyScore[responses.anxiety] || 0) + (frequencyScore[responses.worry] || 0)

    // Generate PDF
    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    const margin = 20
    const contentWidth = pageWidth - margin * 2
    let y = 20

    // --- Header ---
    doc.setFontSize(22)
    doc.setTextColor(78, 155, 185) // primary color
    doc.text('Animoa Wellness Report', margin, y)
    y += 10

    doc.setFontSize(10)
    doc.setTextColor(128, 128, 128)
    const dateStr = new Date(assessment.created_at).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
    doc.text(dateStr, margin, y)
    y += 4
    if (profile?.full_name) {
      doc.text(`Prepared for: ${profile.full_name}`, margin, y)
      y += 4
    }

    // Divider
    y += 4
    doc.setDrawColor(200, 200, 200)
    doc.line(margin, y, pageWidth - margin, y)
    y += 10

    // --- Scores ---
    doc.setFontSize(14)
    doc.setTextColor(49, 80, 94) // secondary color
    doc.text('Assessment Scores', margin, y)
    y += 8

    doc.setFontSize(11)
    doc.setTextColor(60, 60, 60)
    doc.text(`PHQ-2 (Depression Screening): ${phq2} / 6`, margin, y)
    y += 6
    doc.text(`GAD-2 (Anxiety Screening): ${gad2} / 6`, margin, y)
    y += 10

    // --- Responses ---
    doc.setFontSize(14)
    doc.setTextColor(49, 80, 94)
    doc.text('Your Responses', margin, y)
    y += 8

    const responseItems: [string, string][] = [
      ['Feeling down, depressed, or hopeless', responseLabels.mood[responses.mood] || responses.mood],
      ['Little interest or pleasure in doing things', responseLabels.interest[responses.interest] || responses.interest],
      ['Feeling nervous, anxious, or on edge', responseLabels.anxiety[responses.anxiety] || responses.anxiety],
      ['Not being able to stop or control worrying', responseLabels.worry[responses.worry] || responses.worry],
      ['Sleep quality', responseLabels.sleep[responses.sleep] || responses.sleep],
      ['Social support', responseLabels.support[responses.support] || responses.support],
    ]

    if (responses.coping) {
      responseItems.push(['Coping strategies', responses.coping])
    }

    doc.setFontSize(10)
    responseItems.forEach(([question, answer]) => {
      doc.setTextColor(100, 100, 100)
      doc.text(question, margin, y)
      y += 5
      doc.setTextColor(49, 80, 94)
      doc.setFont('helvetica', 'bold')
      doc.text(answer, margin + 4, y)
      doc.setFont('helvetica', 'normal')
      y += 7
    })

    y += 4

    // --- Recommendations ---
    if (recommendations) {
      // Check if we need a new page
      if (y > 220) {
        doc.addPage()
        y = 20
      }

      doc.setFontSize(14)
      doc.setTextColor(49, 80, 94)
      doc.text('Personalized Recommendations', margin, y)
      y += 8

      doc.setFontSize(10)
      doc.setTextColor(60, 60, 60)

      // Wrap and render recommendation text
      const lines = doc.splitTextToSize(recommendations, contentWidth)
      for (const line of lines) {
        if (y > 275) {
          doc.addPage()
          y = 20
        }
        doc.text(line, margin, y)
        y += 5
      }
    }

    // --- Disclaimer ---
    y = Math.max(y + 10, 260)
    if (y > 275) {
      doc.addPage()
      y = 260
    }
    doc.setDrawColor(200, 200, 200)
    doc.line(margin, y, pageWidth - margin, y)
    y += 6
    doc.setFontSize(8)
    doc.setTextColor(150, 150, 150)
    doc.text(
      'Disclaimer: This report is for informational purposes only and is not a substitute for professional',
      margin,
      y
    )
    y += 4
    doc.text(
      'medical advice, diagnosis, or treatment. If you are experiencing a mental health crisis, please contact',
      margin,
      y
    )
    y += 4
    doc.text(
      'the 988 Suicide and Crisis Lifeline (call or text 988) or go to your nearest emergency room.',
      margin,
      y
    )
    y += 6
    doc.text('Generated by Animoa - Your Mental Wellness Companion', margin, y)

    // Return PDF as binary
    const pdfBuffer = Buffer.from(doc.output('arraybuffer'))

    return new NextResponse(pdfBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="animoa-wellness-report-${assessment.id.slice(0, 8)}.pdf"`,
      },
    })
  } catch (error) {
    console.error('PDF generation error:', error)
    return NextResponse.json({ error: 'Failed to generate PDF' }, { status: 500 })
  }
}
